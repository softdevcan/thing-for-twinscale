"""
Twin RDF Service

Converts Twin YAML to RDF triples and stores them in Fuseki twin-db.
Provides SPARQL query capabilities for Twin data.

Usage:
    service = TwinRDFService()
    await service.store_twin_yaml(interface_yaml, instance_yaml, thing_id)
    results = await service.query_interfaces()
"""

import json
import logging
import yaml
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from rdflib import Graph, Literal, URIRef, BNode, Namespace
from rdflib.namespace import RDF, RDFS, XSD

from ..core.config import get_settings
from ..core import (
    TWIN, TWIN_DATA,
    create_interface_uri, create_instance_uri,
    create_property_uri, create_relationship_uri, create_command_uri,
    get_twin_ontology
)
from ..core.exceptions import FusekiException

logger = logging.getLogger(__name__)
settings = get_settings()


class TwinRDFService:
    """Service for managing Twin data in RDF format"""

    def __init__(self, username: str = None, password: str = None):
        """
        Initialize Twin RDF Service

        Args:
            username: Fuseki username (default from settings)
            password: Fuseki password (default from settings)
        """
        self.fuseki_url = settings.FUSEKI_URL
        self.dataset = settings.FUSEKI_DATASET
        self.endpoint = f"{self.fuseki_url}/{self.dataset}"
        self.query_endpoint = f"{self.endpoint}/query"
        self.update_endpoint = f"{self.endpoint}/update"
        self.data_endpoint = f"{self.endpoint}/data"

        self.username = username or settings.FUSEKI_USERNAME
        self.password = password or settings.FUSEKI_PASSWORD

        # Namespaces
        self.TS = TWIN
        self.TSD = TWIN_DATA

        logger.info(f"TwinRDFService initialized with endpoint: {self.endpoint}")

    # ========================================================================
    # Public API - Store Operations
    # ========================================================================

    async def store_twin_yaml(
        self,
        interface_yaml: str,
        instance_yaml: str,
        thing_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store Twin YAML as RDF triples in Fuseki using Named Graph

        Args:
            interface_yaml: TwinInterface YAML string
            instance_yaml: TwinInstance YAML string
            thing_id: Original Thing ID for tracking (used as graph URI)
            metadata: Additional metadata (optional, should include tenant_id)

        Returns:
            bool: True if successful

        Raises:
            FusekiException: If storage fails
        """
        try:
            # Parse YAML
            interface_data = yaml.safe_load(interface_yaml)
            instance_data = yaml.safe_load(instance_yaml)

            # Convert to RDF
            graph = Graph()
            graph.bind("ts", self.TS)
            graph.bind("tsd", self.TSD)
            graph.bind("rdf", RDF)
            graph.bind("rdfs", RDFS)
            graph.bind("xsd", XSD)

            # Add interface triples
            self._add_interface_to_graph(graph, interface_data, metadata)

            # Add instance triples
            self._add_instance_to_graph(graph, instance_data, metadata)

            # Get tenant_id from metadata
            tenant_id = metadata.get("tenant_id", "default") if metadata else "default"

            # Create named graph URI: http://twin.io/graphs/{tenant_id}/{thing_id}
            graph_uri = f"http://twin.io/graphs/{tenant_id}/{thing_id}"

            # Store in Fuseki as Named Graph
            await self._store_named_graph(graph, graph_uri)

            logger.info(f"Successfully stored Twin RDF for thing: {thing_id} in graph: {graph_uri}")
            return True

        except Exception as e:
            logger.error(f"Failed to store Twin RDF: {str(e)}")
            raise FusekiException(f"Failed to store Twin RDF: {str(e)}")

    async def delete_twin(self, interface_name: str, tenant_id: str = "default") -> bool:
        """
        Delete Twin interface and all its instances from Fuseki by dropping the named graph

        Args:
            interface_name: Name of the TwinInterface to delete
            tenant_id: Tenant ID for graph isolation

        Returns:
            bool: True if successful
        """
        try:
            # Construct the thing_id from interface_name (remove iodt2- prefix if present)
            # interface_name format: iodt2-sensor1
            # thing_id format: tenant:sensor1 or just sensor1
            thing_id_part = interface_name.replace("iodt2-", "")

            # Try both formats: with and without tenant prefix
            possible_thing_ids = [
                f"{tenant_id}:{thing_id_part}",
                thing_id_part
            ]

            # Try to find and drop the graph
            for thing_id in possible_thing_ids:
                graph_uri = f"http://twin.io/graphs/{tenant_id}/{thing_id}"

                # DROP GRAPH query
                query = f"""
                DROP SILENT GRAPH <{graph_uri}>
                """

                await self._execute_update(query)
                logger.info(f"Attempted to delete graph: {graph_uri}")

            logger.info(f"Deleted Twin data for interface: {interface_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Twin data: {str(e)}")
            raise FusekiException(f"Failed to delete Twin data: {str(e)}")

    # ========================================================================
    # Public API - Query Operations
    # ========================================================================

    async def query_interfaces(
        self,
        name_filter: Optional[str] = None,
        limit: int = 100,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query all TwinInterfaces from named graphs

        Args:
            name_filter: Optional name filter (substring match)
            limit: Maximum number of results
            tenant_id: Optional tenant filter

        Returns:
            List of interface dictionaries
        """
        try:
            filter_clause = ""
            if name_filter:
                filter_clause = f'FILTER(CONTAINS(LCASE(?name), "{name_filter.lower()}"))'

            # Build tenant graph filter
            graph_filter = self._build_tenant_graph_filter(tenant_id)

            # Query across all named graphs - only TwinInterface, not TwinInstance
            query = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT DISTINCT ?interface ?name ?description ?generatedAt ?graph
            WHERE {{
                GRAPH ?graph {{
                    ?interface a ts:TwinInterface .
                    FILTER NOT EXISTS {{ ?interface a ts:TwinInstance }}
                    ?interface ts:name ?name .
                    OPTIONAL {{ ?interface ts:description ?description }}
                    OPTIONAL {{ ?interface ts:generatedAt ?generatedAt }}
                    {filter_clause}
                }}
                {graph_filter}
            }}
            ORDER BY ?name
            LIMIT {limit}
            """

            results = await self._execute_query(query)
            return self._parse_sparql_results(results)

        except Exception as e:
            logger.error(f"Failed to query interfaces: {str(e)}")
            raise FusekiException(f"Failed to query interfaces: {str(e)}")

    async def query_instances(
        self,
        interface_name: Optional[str] = None,
        limit: int = 100,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query TwinInstances, optionally filtered by interface and tenant

        Args:
            interface_name: Optional interface name filter
            limit: Maximum number of results
            tenant_id: Optional tenant filter

        Returns:
            List of instance dictionaries
        """
        try:
            interface_filter = ""
            if interface_name:
                interface_uri = create_interface_uri(interface_name)
                interface_filter = f"?instance ts:instanceOf <{interface_uri}> ."

            # Add tenant filter if provided
            graph_filter = ""
            if tenant_id:
                graph_filter = f"FILTER(STRSTARTS(STR(?graph), 'http://twin.io/graphs/{tenant_id}/'))"

            query = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT ?instance ?name ?interfaceName ?graph
            WHERE {{
                GRAPH ?graph {{
                    ?instance a ts:TwinInstance .
                    ?instance ts:name ?name .
                    ?instance ts:instanceOf ?interface .
                    ?interface ts:name ?interfaceName .
                    {interface_filter}
                }}
                {graph_filter}
            }}
            ORDER BY ?name
            LIMIT {limit}
            """

            results = await self._execute_query(query)
            return self._parse_sparql_results(results)

        except Exception as e:
            logger.error(f"Failed to query instances: {str(e)}")
            raise FusekiException(f"Failed to query instances: {str(e)}")

    async def get_interface_details(self, interface_name: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a TwinInterface including properties, relationships, commands

        Args:
            interface_name: Name of the interface
            tenant_id: Optional tenant filter

        Returns:
            Dictionary with interface details or None if not found
        """
        try:
            interface_uri = create_interface_uri(interface_name)

            # Add tenant filter if provided
            graph_filter = ""
            if tenant_id:
                graph_filter = f"FILTER(STRSTARTS(STR(?graph), 'http://twin.io/graphs/{tenant_id}/'))"

            query = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT ?name ?description ?generatedAt ?generatedBy
                   ?propName ?propType ?propDesc ?writable
                   ?relName ?relTarget ?relDesc
                   ?cmdName ?cmdDesc ?graph
            WHERE {{
                GRAPH ?graph {{
                    <{interface_uri}> a ts:TwinInterface .
                    <{interface_uri}> ts:name ?name .
                    OPTIONAL {{ <{interface_uri}> ts:description ?description }}
                    OPTIONAL {{ <{interface_uri}> ts:generatedAt ?generatedAt }}
                    OPTIONAL {{ <{interface_uri}> ts:generatedBy ?generatedBy }}

                    # Properties
                    OPTIONAL {{
                        <{interface_uri}> ts:hasProperty ?prop .
                        ?prop ts:propertyName ?propName .
                        ?prop ts:propertyType ?propType .
                        OPTIONAL {{ ?prop ts:description ?propDesc }}
                        OPTIONAL {{ ?prop ts:writable ?writable }}
                    }}

                    # Relationships
                    OPTIONAL {{
                        <{interface_uri}> ts:hasRelationship ?rel .
                        ?rel ts:relationshipName ?relName .
                        ?rel ts:targetInterface ?relTarget .
                        OPTIONAL {{ ?rel ts:description ?relDesc }}
                    }}

                    # Commands
                    OPTIONAL {{
                        <{interface_uri}> ts:hasCommand ?cmd .
                        ?cmd ts:commandName ?cmdName .
                        OPTIONAL {{ ?cmd ts:description ?cmdDesc }}
                    }}
                }}
                {graph_filter}
            }}
            """

            results = await self._execute_query(query)
            return self._parse_interface_details(results)

        except Exception as e:
            logger.error(f"Failed to get interface details: {str(e)}")
            raise FusekiException(f"Failed to get interface details: {str(e)}")

    async def search(
        self,
        query: str,
        tenant_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Full-text search across TwinInterfaces and TwinInstances.

        Searches by name, description, original ID, property names, and graph URI.

        Args:
            query: Search string (substring match, case-insensitive)
            tenant_id: Optional tenant filter
            limit: Maximum number of results

        Returns:
            List of matching items with id, name, type, description, graph
        """
        try:
            graph_filter = self._build_tenant_graph_filter(tenant_id)

            safe_query = query.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
            lc_query = safe_query.lower()

            # Use UNION pattern to search across different fields
            # This avoids issues with OPTIONAL + FILTER interactions in Fuseki
            sparql = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT DISTINCT ?uri ?name ?type ?description ?graph ?originalId ?thingType
            WHERE {{
                GRAPH ?graph {{
                    ?uri ts:name ?name .
                    ?uri a ?type .
                    FILTER(?type IN (ts:TwinInterface, ts:TwinInstance))
                    OPTIONAL {{ ?uri ts:description ?description }}
                    OPTIONAL {{ ?uri ts:originalId ?originalId }}
                    OPTIONAL {{ ?uri ts:thingType ?thingType }}
                }}
                {graph_filter}
                FILTER(
                    CONTAINS(LCASE(STR(?name)), "{lc_query}")
                    || CONTAINS(LCASE(STR(?graph)), "{lc_query}")
                    || (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "{lc_query}"))
                    || (BOUND(?originalId) && CONTAINS(LCASE(STR(?originalId)), "{lc_query}"))
                )
            }}
            ORDER BY ?name
            LIMIT {limit}
            """

            results = await self._execute_query(sparql)
            parsed = self._parse_sparql_results(results)

            # Normalize results for frontend consumption
            items = []
            for row in parsed:
                item = {
                    "id": row.get("uri", ""),
                    "name": row.get("name", ""),
                    "type": "TwinInterface" if "TwinInterface" in row.get("type", "") else "TwinInstance",
                    "description": row.get("description"),
                    "graph": row.get("graph", ""),
                    "originalId": row.get("originalId"),
                    "thingType": row.get("thingType"),
                }
                items.append(item)
            return items

        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            raise FusekiException(f"Failed to search: {str(e)}")

    async def get_all_things(
        self,
        page: int = 1,
        page_size: int = 10,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all TwinInterfaces and TwinInstances with pagination.

        Args:
            page: Page number (1-based)
            page_size: Items per page
            tenant_id: Optional tenant filter

        Returns:
            Dict with items list and pagination info
        """
        try:
            graph_filter = self._build_tenant_graph_filter(tenant_id)

            offset = (page - 1) * page_size

            query = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT ?uri ?name ?type ?description ?graph ?originalId ?thingType
            WHERE {{
                GRAPH ?graph {{
                    ?uri ts:name ?name .
                    ?uri a ?type .
                    FILTER(?type IN (ts:TwinInterface, ts:TwinInstance))
                    OPTIONAL {{ ?uri ts:description ?description }}
                    OPTIONAL {{ ?uri ts:originalId ?originalId }}
                    OPTIONAL {{ ?uri ts:thingType ?thingType }}
                }}
                {graph_filter}
            }}
            ORDER BY ?name
            OFFSET {offset}
            LIMIT {page_size}
            """

            results = await self._execute_query(query)
            parsed = self._parse_sparql_results(results)

            items = []
            for row in parsed:
                item = {
                    "id": row.get("uri", ""),
                    "name": row.get("name", ""),
                    "type": "TwinInterface" if "TwinInterface" in row.get("type", "") else "TwinInstance",
                    "description": row.get("description"),
                    "graph": row.get("graph", ""),
                    "originalId": row.get("originalId"),
                    "thingType": row.get("thingType"),
                }
                items.append(item)

            return {
                "items": items,
                "pagination": {
                    "page": page,
                    "pageSize": page_size,
                    "total": len(items)
                }
            }

        except Exception as e:
            logger.error(f"Failed to get all things: {str(e)}")
            raise FusekiException(f"Failed to get all things: {str(e)}")

    async def get_thing_by_id(
        self,
        thing_id: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single thing (interface or instance) by its URI or name.

        Args:
            thing_id: Thing URI or name
            tenant_id: Optional tenant filter

        Returns:
            Thing details or None
        """
        try:
            graph_filter = self._build_tenant_graph_filter(tenant_id)

            safe_id = thing_id.replace('"', '\\"')

            query = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT ?uri ?name ?type ?description ?graph ?originalId ?thingType
                   ?propName ?propType ?propDesc
            WHERE {{
                GRAPH ?graph {{
                    ?uri a ?type .
                    ?uri ts:name ?name .
                    FILTER(?type IN (ts:TwinInterface, ts:TwinInstance))
                    FILTER(
                        STR(?uri) = "{safe_id}"
                        || STR(?name) = "{safe_id}"
                        || CONTAINS(STR(?graph), "{safe_id}")
                    )
                    OPTIONAL {{ ?uri ts:description ?description }}
                    OPTIONAL {{ ?uri ts:originalId ?originalId }}
                    OPTIONAL {{ ?uri ts:thingType ?thingType }}
                    OPTIONAL {{
                        ?uri ts:hasProperty ?prop .
                        ?prop ts:propertyName ?propName .
                        ?prop ts:propertyType ?propType .
                        OPTIONAL {{ ?prop ts:description ?propDesc }}
                    }}
                }}
                {graph_filter}
            }}
            """

            results = await self._execute_query(query)
            parsed = self._parse_sparql_results(results)

            if not parsed:
                return None

            first = parsed[0]
            thing = {
                "id": first.get("uri", ""),
                "@id": first.get("originalId") or first.get("name", ""),
                "name": first.get("name", ""),
                "title": first.get("name", ""),
                "type": "TwinInterface" if "TwinInterface" in first.get("type", "") else "TwinInstance",
                "description": first.get("description"),
                "graph": first.get("graph", ""),
                "thingType": first.get("thingType"),
                "properties": {}
            }

            seen_props = set()
            for row in parsed:
                prop_name = row.get("propName")
                if prop_name and prop_name not in seen_props:
                    thing["properties"][prop_name] = {
                        "type": row.get("propType", "string"),
                        "description": row.get("propDesc"),
                    }
                    seen_props.add(prop_name)

            return thing

        except Exception as e:
            logger.error(f"Failed to get thing by id: {str(e)}")
            raise FusekiException(f"Failed to get thing by id: {str(e)}")

    async def check_health(self) -> Dict[str, Any]:
        """Check Fuseki connection health"""
        try:
            query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o } LIMIT 1"
            results = await self._execute_query(query)
            parsed = self._parse_sparql_results(results)
            triple_count = parsed[0].get("count", "0") if parsed else "0"

            return {
                "status": "healthy",
                "fuseki_url": self.fuseki_url,
                "dataset": self.dataset,
                "triple_count": triple_count
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "fuseki_url": self.fuseki_url,
                "dataset": self.dataset
            }

    async def search_by_property(
        self,
        property_name: str,
        operator: str = "eq",
        value: float = 0,
        tenant_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search TwinInterfaces by property schema criteria.

        Finds interfaces that have a matching property and optionally
        filters by the property's min/max range defined in the schema.

        Args:
            property_name: Property name to search for (e.g., 'temperature')
            operator: Comparison operator ('gt', 'gte', 'lt', 'lte', 'eq', 'ne')
            value: Threshold value to compare against property min/max
            tenant_id: Optional tenant filter
            limit: Maximum results

        Returns:
            Dict with results list, count, and metadata
        """
        import time
        start_time = time.time()

        try:
            graph_filter = self._build_tenant_graph_filter(tenant_id)
            safe_prop = property_name.replace('"', '\\"').lower()

            # Build the value filter based on operator
            # We compare against the property's min/max range in the schema
            value_filter = ""
            if operator == "gt":
                value_filter = f"&& (?propMax > {value} || !BOUND(?propMax))"
            elif operator == "gte":
                value_filter = f"&& (?propMax >= {value} || !BOUND(?propMax))"
            elif operator == "lt":
                value_filter = f"&& (?propMin < {value} || !BOUND(?propMin))"
            elif operator == "lte":
                value_filter = f"&& (?propMin <= {value} || !BOUND(?propMin))"
            elif operator == "eq":
                value_filter = f"&& (?propMin <= {value} || !BOUND(?propMin)) && (?propMax >= {value} || !BOUND(?propMax))"

            sparql = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT DISTINCT ?interface ?name ?propName ?propType ?propMin ?propMax ?unit ?description ?graph ?thingType
            WHERE {{
                GRAPH ?graph {{
                    ?interface a ts:TwinInterface .
                    ?interface ts:name ?name .
                    ?interface ts:hasProperty ?prop .
                    ?prop ts:propertyName ?propName .
                    ?prop ts:propertyType ?propType .
                    FILTER(CONTAINS(LCASE(STR(?propName)), "{safe_prop}"))
                    OPTIONAL {{ ?prop ts:minimum ?propMin }}
                    OPTIONAL {{ ?prop ts:maximum ?propMax }}
                    OPTIONAL {{ ?prop ts:unit ?unit }}
                    OPTIONAL {{ ?interface ts:description ?description }}
                    OPTIONAL {{ ?interface ts:thingType ?thingType }}
                }}
                {graph_filter}
                FILTER(true {value_filter})
            }}
            ORDER BY ?name
            LIMIT {limit}
            """

            results = await self._execute_query(sparql)
            parsed = self._parse_sparql_results(results)

            items = []
            for row in parsed:
                items.append({
                    "thingId": row.get("interface", ""),
                    "name": row.get("name", ""),
                    "property": row.get("propName", ""),
                    "propertyType": row.get("propType", ""),
                    "min": row.get("propMin"),
                    "max": row.get("propMax"),
                    "unit": row.get("unit"),
                    "description": row.get("description"),
                    "thingType": row.get("thingType"),
                    "graph": row.get("graph", ""),
                })

            elapsed_ms = round((time.time() - start_time) * 1000, 1)

            return {
                "results": items,
                "count": len(items),
                "schema_matches": len(items),
                "value_matches": len(items),
                "query_time_ms": elapsed_ms,
                "property": property_name,
                "operator": operator,
                "value": value,
            }

        except Exception as e:
            logger.error(f"Failed to search by property: {str(e)}")
            raise FusekiException(f"Failed to search by property: {str(e)}")

    async def get_instance_relationships(
        self,
        instance_name: str,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all relationships for a TwinInstance

        Args:
            instance_name: Name of the instance
            tenant_id: Optional tenant filter

        Returns:
            List of relationship dictionaries
        """
        try:
            instance_uri = create_instance_uri(instance_name)

            # Add tenant filter if provided
            graph_filter = ""
            if tenant_id:
                graph_filter = f"FILTER(STRSTARTS(STR(?graph), 'http://twin.io/graphs/{tenant_id}/'))"

            query = f"""
            PREFIX ts: <{self.TS}>
            PREFIX tsd: <{self.TSD}>

            SELECT ?relName ?targetInstance ?targetInterface ?graph
            WHERE {{
                GRAPH ?graph {{
                    <{instance_uri}> ts:hasInstanceRelationship ?rel .
                    ?rel ts:relationshipName ?relName .
                    ?rel ts:targetInstance ?target .
                    ?target ts:name ?targetInstance .
                    ?target ts:instanceOf ?interface .
                    ?interface ts:name ?targetInterface .
                }}
                {graph_filter}
            }}
            """

            results = await self._execute_query(query)
            return self._parse_sparql_results(results)

        except Exception as e:
            logger.error(f"Failed to get instance relationships: {str(e)}")
            raise FusekiException(f"Failed to get instance relationships: {str(e)}")

    # ========================================================================
    # Private Helper Methods - Tenant Filtering
    # ========================================================================

    def _build_tenant_graph_filter(self, tenant_id: Optional[str] = None) -> str:
        """
        Build a SPARQL FILTER clause for tenant-based graph filtering.

        When a specific tenant is provided, includes both that tenant's graphs
        and the 'default' tenant graphs (since things may be stored under default).
        """
        if not tenant_id or tenant_id == "default":
            return ""
        return (
            f"FILTER("
            f"STRSTARTS(STR(?graph), 'http://twin.io/graphs/{tenant_id}/') "
            f"|| STRSTARTS(STR(?graph), 'http://twin.io/graphs/default/')"
            f")"
        )

    # ========================================================================
    # Private Helper Methods - RDF Conversion
    # ========================================================================

    def _add_interface_to_graph(
        self,
        graph: Graph,
        interface_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add TwinInterface to RDF graph"""
        interface_name = interface_data["metadata"]["name"]
        interface_uri = create_interface_uri(interface_name)

        # Interface type
        graph.add((interface_uri, RDF.type, self.TS.TwinInterface))
        graph.add((interface_uri, self.TS.name, Literal(interface_name)))

        # Metadata
        if "labels" in interface_data["metadata"]:
            labels = interface_data["metadata"]["labels"]
            if "generated-by" in labels:
                graph.add((interface_uri, self.TS.generatedBy, Literal(labels["generated-by"])))
            if "generated-at" in labels:
                graph.add((interface_uri, self.TS.generatedAt,
                          Literal(labels["generated-at"], datatype=XSD.dateTime)))
            # NEW: Thing Type
            if "thing-type" in labels:
                graph.add((interface_uri, self.TS.thingType, Literal(labels["thing-type"])))

        if "annotations" in interface_data["metadata"]:
            annotations = interface_data["metadata"]["annotations"]
            if "source" in annotations:
                graph.add((interface_uri, self.TS.sourceFormat, Literal(annotations["source"])))
            if "original-id" in annotations:
                graph.add((interface_uri, self.TS.originalId, Literal(annotations["original-id"])))
            # NEW: Domain Metadata
            if "manufacturer" in annotations:
                graph.add((interface_uri, self.TS.manufacturer, Literal(annotations["manufacturer"])))
            if "model" in annotations:
                graph.add((interface_uri, self.TS.model, Literal(annotations["model"])))
            if "serialNumber" in annotations:
                graph.add((interface_uri, self.TS.serialNumber, Literal(annotations["serialNumber"])))
            if "firmwareVersion" in annotations:
                graph.add((interface_uri, self.TS.firmwareVersion, Literal(annotations["firmwareVersion"])))
            # NEW: DTDL Metadata
            if "dtdl-interface" in annotations:
                graph.add((interface_uri, self.TS.dtdlInterface, Literal(annotations["dtdl-interface"])))
            if "dtdl-interface-name" in annotations:
                graph.add((interface_uri, self.TS.dtdlInterfaceName, Literal(annotations["dtdl-interface-name"])))
            if "dtdl-category" in annotations:
                graph.add((interface_uri, self.TS.dtdlCategory, Literal(annotations["dtdl-category"])))

        spec = interface_data.get("spec", {})

        # Properties
        for prop in spec.get("properties", []):
            prop_uri = create_property_uri(interface_name, prop["name"])
            graph.add((prop_uri, RDF.type, self.TS.Property))
            graph.add((prop_uri, self.TS.propertyName, Literal(prop["name"])))
            graph.add((prop_uri, self.TS.propertyType, Literal(prop["type"])))

            if "description" in prop and prop["description"]:
                graph.add((prop_uri, self.TS.description, Literal(prop["description"])))
            if "x-writable" in prop:
                graph.add((prop_uri, self.TS.writable, Literal(prop["x-writable"], datatype=XSD.boolean)))
            if "x-minimum" in prop and prop["x-minimum"] is not None:
                graph.add((prop_uri, self.TS.minimum, Literal(prop["x-minimum"])))
            if "x-maximum" in prop and prop["x-maximum"] is not None:
                graph.add((prop_uri, self.TS.maximum, Literal(prop["x-maximum"])))
            if "x-unit" in prop and prop["x-unit"]:
                graph.add((prop_uri, self.TS.unit, Literal(prop["x-unit"])))

            graph.add((interface_uri, self.TS.hasProperty, prop_uri))

        # Relationships
        for rel in spec.get("relationships", []):
            rel_uri = create_relationship_uri(interface_name, rel["name"])
            graph.add((rel_uri, RDF.type, self.TS.Relationship))
            graph.add((rel_uri, self.TS.relationshipName, Literal(rel["name"])))
            graph.add((rel_uri, self.TS.targetInterface, Literal(rel["interface"])))

            if "description" in rel and rel["description"]:
                graph.add((rel_uri, self.TS.description, Literal(rel["description"])))

            graph.add((interface_uri, self.TS.hasRelationship, rel_uri))

        # Commands
        for cmd in spec.get("commands", []):
            cmd_uri = create_command_uri(interface_name, cmd["name"])
            graph.add((cmd_uri, RDF.type, self.TS.Command))
            graph.add((cmd_uri, self.TS.commandName, Literal(cmd["name"])))

            if "description" in cmd and cmd["description"]:
                graph.add((cmd_uri, self.TS.description, Literal(cmd["description"])))
            if "schema" in cmd:
                graph.add((cmd_uri, self.TS.schema, Literal(json.dumps(cmd["schema"]))))

            graph.add((interface_uri, self.TS.hasCommand, cmd_uri))

    def _add_instance_to_graph(
        self,
        graph: Graph,
        instance_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add TwinInstance to RDF graph"""
        instance_name = instance_data["metadata"]["name"]
        instance_uri = create_instance_uri(instance_name)

        # Instance type
        graph.add((instance_uri, RDF.type, self.TS.TwinInstance))
        graph.add((instance_uri, self.TS.name, Literal(instance_name)))

        # Interface reference
        interface_name = instance_data["spec"]["interface"]
        interface_uri = create_interface_uri(interface_name)
        graph.add((instance_uri, self.TS.instanceOf, interface_uri))

        # Metadata
        if "labels" in instance_data["metadata"]:
            labels = instance_data["metadata"]["labels"]
            if "generated-by" in labels:
                graph.add((instance_uri, self.TS.generatedBy, Literal(labels["generated-by"])))
            if "generated-at" in labels:
                graph.add((instance_uri, self.TS.generatedAt,
                          Literal(labels["generated-at"], datatype=XSD.dateTime)))

        # Instance relationships
        for rel in instance_data["spec"].get("twinInstanceRelationships", []):
            rel_node = BNode()
            graph.add((rel_node, RDF.type, self.TS.InstanceRelationship))
            graph.add((rel_node, self.TS.relationshipName, Literal(rel["name"])))

            target_instance_uri = create_instance_uri(rel["instance"])
            graph.add((rel_node, self.TS.targetInstance, target_instance_uri))

            graph.add((instance_uri, self.TS.hasInstanceRelationship, rel_node))

    # ========================================================================
    # Private Helper Methods - Fuseki Communication
    # ========================================================================

    async def _store_graph(self, graph: Graph):
        """Store RDF graph in Fuseki default graph (deprecated - use _store_named_graph)"""
        try:
            # Serialize to Turtle
            turtle_data = graph.serialize(format="turtle")

            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.username, self.password)
                headers = {"Content-Type": "text/turtle"}

                async with session.post(
                    self.data_endpoint,
                    data=turtle_data,
                    headers=headers,
                    auth=auth
                ) as response:
                    if response.status not in [200, 201, 204]:
                        error_text = await response.text()
                        raise FusekiException(
                            f"Failed to store graph: {response.status} - {error_text}"
                        )

        except Exception as e:
            logger.error(f"Failed to store graph in Fuseki: {str(e)}")
            raise

    async def _store_named_graph(self, graph: Graph, graph_uri: str):
        """
        Store RDF graph in Fuseki as a Named Graph

        Args:
            graph: RDF graph to store
            graph_uri: URI of the named graph (e.g., http://twin.io/graphs/tenant1/thing1)
        """
        try:
            # Serialize to Turtle
            turtle_data = graph.serialize(format="turtle")

            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.username, self.password)
                headers = {"Content-Type": "text/turtle"}

                # Use PUT to create/replace named graph
                # Fuseki endpoint: /data?graph=<uri>
                named_graph_endpoint = f"{self.data_endpoint}?graph={graph_uri}"

                async with session.put(
                    named_graph_endpoint,
                    data=turtle_data,
                    headers=headers,
                    auth=auth
                ) as response:
                    if response.status not in [200, 201, 204]:
                        error_text = await response.text()
                        raise FusekiException(
                            f"Failed to store named graph: {response.status} - {error_text}"
                        )

                    logger.info(f"Successfully stored named graph: {graph_uri}")

        except Exception as e:
            logger.error(f"Failed to store named graph in Fuseki: {str(e)}")
            raise

    async def _execute_query(self, query: str) -> Dict[str, Any]:
        """Execute SPARQL SELECT query"""
        try:
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.username, self.password)
                headers = {"Accept": "application/sparql-results+json"}

                async with session.post(
                    self.query_endpoint,
                    data={"query": query},
                    headers=headers,
                    auth=auth
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise FusekiException(
                            f"SPARQL query failed: {response.status} - {error_text}"
                        )

                    return await response.json()

        except Exception as e:
            logger.error(f"Failed to execute SPARQL query: {str(e)}")
            raise

    async def _execute_update(self, update: str):
        """Execute SPARQL UPDATE query"""
        try:
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.username, self.password)
                headers = {"Content-Type": "application/sparql-update"}

                async with session.post(
                    self.update_endpoint,
                    data=update,
                    headers=headers,
                    auth=auth
                ) as response:
                    if response.status not in [200, 204]:
                        error_text = await response.text()
                        raise FusekiException(
                            f"SPARQL update failed: {response.status} - {error_text}"
                        )

        except Exception as e:
            logger.error(f"Failed to execute SPARQL update: {str(e)}")
            raise

    # ========================================================================
    # Private Helper Methods - Result Parsing
    # ========================================================================

    def _parse_sparql_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse SPARQL JSON results into list of dictionaries"""
        parsed = []
        for binding in results.get("results", {}).get("bindings", []):
            row = {}
            for var, value in binding.items():
                row[var] = value.get("value")
            parsed.append(row)
        return parsed

    def _parse_interface_details(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse interface details from SPARQL results"""
        bindings = results.get("results", {}).get("bindings", [])
        if not bindings:
            return None

        # First binding has basic info
        first = bindings[0]
        interface = {
            "name": first.get("name", {}).get("value"),
            "description": first.get("description", {}).get("value"),
            "generatedAt": first.get("generatedAt", {}).get("value"),
            "generatedBy": first.get("generatedBy", {}).get("value"),
            "properties": [],
            "relationships": [],
            "commands": []
        }

        # Collect properties, relationships, commands
        seen_props = set()
        seen_rels = set()
        seen_cmds = set()

        for binding in bindings:
            # Properties
            if "propName" in binding:
                prop_name = binding["propName"]["value"]
                if prop_name not in seen_props:
                    interface["properties"].append({
                        "name": prop_name,
                        "type": binding.get("propType", {}).get("value"),
                        "description": binding.get("propDesc", {}).get("value"),
                        "writable": binding.get("writable", {}).get("value") == "true"
                    })
                    seen_props.add(prop_name)

            # Relationships
            if "relName" in binding:
                rel_name = binding["relName"]["value"]
                if rel_name not in seen_rels:
                    interface["relationships"].append({
                        "name": rel_name,
                        "targetInterface": binding.get("relTarget", {}).get("value"),
                        "description": binding.get("relDesc", {}).get("value")
                    })
                    seen_rels.add(rel_name)

            # Commands
            if "cmdName" in binding:
                cmd_name = binding["cmdName"]["value"]
                if cmd_name not in seen_cmds:
                    interface["commands"].append({
                        "name": cmd_name,
                        "description": binding.get("cmdDesc", {}).get("value")
                    })
                    seen_cmds.add(cmd_name)

        return interface


# ============================================================================
# Convenience Functions
# ============================================================================

def create_twin_rdf_service() -> TwinRDFService:
    """Factory function to create TwinRDFService with default settings"""
    return TwinRDFService()


__all__ = [
    "TwinRDFService",
    "create_twin_rdf_service",
]
