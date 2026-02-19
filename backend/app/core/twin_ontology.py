"""
Twin Framework RDF Ontology Definition

This module defines the RDF ontology for Twin Framework.
It provides namespace definitions and helper functions for working with Twin RDF data.

Ontology URI: http://twin.dtd/ontology#
Namespace Prefix: ts

Classes:
- TwinInterface: Blueprint/template for digital twins
- TwinInstance: Concrete instance of a digital twin
- Property: Data property of an interface
- Relationship: Link between interfaces
- Command: Actionable command on an interface

Properties:
- hasProperty: Links interface to its properties
- hasRelationship: Links interface to its relationships
- hasCommand: Links interface to its commands
- instanceOf: Links instance to its interface
- hasInstanceRelationship: Links instance to another instance
"""

from rdflib import Namespace, Graph, RDF, RDFS, XSD, Literal, URIRef
from typing import Dict, Any


# ============================================================================
# Namespace Definitions
# ============================================================================

# Twin Ontology
TWIN = Namespace("http://twin.dtd/ontology#")
TS = TWIN  # Alias

# Twin Data (instances)
TWIN_DATA = Namespace("http://iodt2.com/")
TSD = TWIN_DATA  # Alias

# Standard namespaces
# RDF, RDFS, XSD are imported from rdflib


# ============================================================================
# Ontology Definition
# ============================================================================

def get_twin_ontology() -> Graph:
    """
    Returns the Twin ontology as an RDF Graph.

    This ontology defines the vocabulary for describing Twin Framework
    interfaces and instances in RDF format.

    Returns:
        Graph: RDFLib graph containing the ontology
    """
    g = Graph()

    # Bind namespaces
    g.bind("ts", TWIN)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # ========================================================================
    # Classes
    # ========================================================================

    # TwinInterface Class
    g.add((TWIN.TwinInterface, RDF.type, RDFS.Class))
    g.add((TWIN.TwinInterface, RDFS.label, Literal("Twin Interface", lang="en")))
    g.add((TWIN.TwinInterface, RDFS.comment,
           Literal("A blueprint or template for digital twins", lang="en")))

    # TwinInstance Class
    g.add((TWIN.TwinInstance, RDF.type, RDFS.Class))
    g.add((TWIN.TwinInstance, RDFS.label, Literal("Twin Instance", lang="en")))
    g.add((TWIN.TwinInstance, RDFS.comment,
           Literal("A concrete instance of a digital twin", lang="en")))

    # Property Class
    g.add((TWIN.Property, RDF.type, RDFS.Class))
    g.add((TWIN.Property, RDFS.label, Literal("Property", lang="en")))
    g.add((TWIN.Property, RDFS.comment,
           Literal("A data property of a twin interface", lang="en")))

    # Relationship Class
    g.add((TWIN.Relationship, RDF.type, RDFS.Class))
    g.add((TWIN.Relationship, RDFS.label, Literal("Relationship", lang="en")))
    g.add((TWIN.Relationship, RDFS.comment,
           Literal("A relationship between twin interfaces", lang="en")))

    # Command Class
    g.add((TWIN.Command, RDF.type, RDFS.Class))
    g.add((TWIN.Command, RDFS.label, Literal("Command", lang="en")))
    g.add((TWIN.Command, RDFS.comment,
           Literal("An actionable command on a twin interface", lang="en")))

    # InstanceRelationship Class
    g.add((TWIN.InstanceRelationship, RDF.type, RDFS.Class))
    g.add((TWIN.InstanceRelationship, RDFS.label, Literal("Instance Relationship", lang="en")))
    g.add((TWIN.InstanceRelationship, RDFS.comment,
           Literal("A relationship between twin instances", lang="en")))

    # ========================================================================
    # Properties - Interface Structure
    # ========================================================================

    # hasProperty
    g.add((TWIN.hasProperty, RDF.type, RDF.Property))
    g.add((TWIN.hasProperty, RDFS.label, Literal("has property", lang="en")))
    g.add((TWIN.hasProperty, RDFS.domain, TWIN.TwinInterface))
    g.add((TWIN.hasProperty, RDFS.range, TWIN.Property))

    # hasRelationship
    g.add((TWIN.hasRelationship, RDF.type, RDF.Property))
    g.add((TWIN.hasRelationship, RDFS.label, Literal("has relationship", lang="en")))
    g.add((TWIN.hasRelationship, RDFS.domain, TWIN.TwinInterface))
    g.add((TWIN.hasRelationship, RDFS.range, TWIN.Relationship))

    # hasCommand
    g.add((TWIN.hasCommand, RDF.type, RDF.Property))
    g.add((TWIN.hasCommand, RDFS.label, Literal("has command", lang="en")))
    g.add((TWIN.hasCommand, RDFS.domain, TWIN.TwinInterface))
    g.add((TWIN.hasCommand, RDFS.range, TWIN.Command))

    # ========================================================================
    # Properties - Instance Structure
    # ========================================================================

    # instanceOf
    g.add((TWIN.instanceOf, RDF.type, RDF.Property))
    g.add((TWIN.instanceOf, RDFS.label, Literal("instance of", lang="en")))
    g.add((TWIN.instanceOf, RDFS.domain, TWIN.TwinInstance))
    g.add((TWIN.instanceOf, RDFS.range, TWIN.TwinInterface))

    # hasInstanceRelationship
    g.add((TWIN.hasInstanceRelationship, RDF.type, RDF.Property))
    g.add((TWIN.hasInstanceRelationship, RDFS.label, Literal("has instance relationship", lang="en")))
    g.add((TWIN.hasInstanceRelationship, RDFS.domain, TWIN.TwinInstance))
    g.add((TWIN.hasInstanceRelationship, RDFS.range, TWIN.InstanceRelationship))

    # ========================================================================
    # Properties - Metadata
    # ========================================================================

    # name
    g.add((TWIN.name, RDF.type, RDF.Property))
    g.add((TWIN.name, RDFS.label, Literal("name", lang="en")))
    g.add((TWIN.name, RDFS.range, XSD.string))

    # description
    g.add((TWIN.description, RDF.type, RDF.Property))
    g.add((TWIN.description, RDFS.label, Literal("description", lang="en")))
    g.add((TWIN.description, RDFS.range, XSD.string))

    # ========================================================================
    # Properties - Property Attributes
    # ========================================================================

    # propertyName
    g.add((TWIN.propertyName, RDF.type, RDF.Property))
    g.add((TWIN.propertyName, RDFS.domain, TWIN.Property))
    g.add((TWIN.propertyName, RDFS.range, XSD.string))

    # propertyType
    g.add((TWIN.propertyType, RDF.type, RDF.Property))
    g.add((TWIN.propertyType, RDFS.domain, TWIN.Property))
    g.add((TWIN.propertyType, RDFS.range, XSD.string))

    # writable
    g.add((TWIN.writable, RDF.type, RDF.Property))
    g.add((TWIN.writable, RDFS.domain, TWIN.Property))
    g.add((TWIN.writable, RDFS.range, XSD.boolean))

    # minimum
    g.add((TWIN.minimum, RDF.type, RDF.Property))
    g.add((TWIN.minimum, RDFS.domain, TWIN.Property))

    # maximum
    g.add((TWIN.maximum, RDF.type, RDF.Property))
    g.add((TWIN.maximum, RDFS.domain, TWIN.Property))

    # unit
    g.add((TWIN.unit, RDF.type, RDF.Property))
    g.add((TWIN.unit, RDFS.domain, TWIN.Property))
    g.add((TWIN.unit, RDFS.range, XSD.string))

    # ========================================================================
    # Properties - Relationship Attributes
    # ========================================================================

    # relationshipName
    g.add((TWIN.relationshipName, RDF.type, RDF.Property))
    g.add((TWIN.relationshipName, RDFS.domain, TWIN.Relationship))
    g.add((TWIN.relationshipName, RDFS.range, XSD.string))

    # targetInterface
    g.add((TWIN.targetInterface, RDF.type, RDF.Property))
    g.add((TWIN.targetInterface, RDFS.domain, TWIN.Relationship))
    g.add((TWIN.targetInterface, RDFS.range, XSD.string))

    # ========================================================================
    # Properties - Command Attributes
    # ========================================================================

    # commandName
    g.add((TWIN.commandName, RDF.type, RDF.Property))
    g.add((TWIN.commandName, RDFS.domain, TWIN.Command))
    g.add((TWIN.commandName, RDFS.range, XSD.string))

    # schema
    g.add((TWIN.schema, RDF.type, RDF.Property))
    g.add((TWIN.schema, RDFS.domain, TWIN.Command))
    g.add((TWIN.schema, RDFS.range, XSD.string))  # JSON string

    # ========================================================================
    # Properties - Instance Relationship Attributes
    # ========================================================================

    # targetInstance
    g.add((TWIN.targetInstance, RDF.type, RDF.Property))
    g.add((TWIN.targetInstance, RDFS.domain, TWIN.InstanceRelationship))
    g.add((TWIN.targetInstance, RDFS.range, TWIN.TwinInstance))

    # ========================================================================
    # Properties - Provenance
    # ========================================================================

    # generatedBy
    g.add((TWIN.generatedBy, RDF.type, RDF.Property))
    g.add((TWIN.generatedBy, RDFS.label, Literal("generated by", lang="en")))
    g.add((TWIN.generatedBy, RDFS.range, XSD.string))

    # generatedAt
    g.add((TWIN.generatedAt, RDF.type, RDF.Property))
    g.add((TWIN.generatedAt, RDFS.label, Literal("generated at", lang="en")))
    g.add((TWIN.generatedAt, RDFS.range, XSD.dateTime))

    # sourceFormat
    g.add((TWIN.sourceFormat, RDF.type, RDF.Property))
    g.add((TWIN.sourceFormat, RDFS.label, Literal("source format", lang="en")))
    g.add((TWIN.sourceFormat, RDFS.range, XSD.string))

    # originalId
    g.add((TWIN.originalId, RDF.type, RDF.Property))
    g.add((TWIN.originalId, RDFS.label, Literal("original ID", lang="en")))
    g.add((TWIN.originalId, RDFS.range, XSD.string))

    return g


# ============================================================================
# Helper Functions
# ============================================================================

def create_interface_uri(interface_name: str) -> URIRef:
    """Create URI for a TwinInterface"""
    return URIRef(f"{TWIN_DATA}{interface_name}")


def create_instance_uri(instance_name: str) -> URIRef:
    """Create URI for a TwinInstance"""
    return URIRef(f"{TWIN_DATA}instance/{instance_name}")


def create_property_uri(interface_name: str, property_name: str) -> URIRef:
    """Create URI for a Property"""
    return URIRef(f"{TWIN_DATA}{interface_name}/property/{property_name}")


def create_relationship_uri(interface_name: str, relationship_name: str) -> URIRef:
    """Create URI for a Relationship"""
    return URIRef(f"{TWIN_DATA}{interface_name}/relationship/{relationship_name}")


def create_command_uri(interface_name: str, command_name: str) -> URIRef:
    """Create URI for a Command"""
    return URIRef(f"{TWIN_DATA}{interface_name}/command/{command_name}")


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "TWIN",
    "TS",
    "TWIN_DATA",
    "TSD",
    "get_twin_ontology",
    "create_interface_uri",
    "create_instance_uri",
    "create_property_uri",
    "create_relationship_uri",
    "create_command_uri",
]
