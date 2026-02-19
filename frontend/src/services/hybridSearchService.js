/**
 * Hybrid Search Service
 * Searches Twin RDF for things by property schema criteria
 */

import axiosInstance from "./axios";

/**
 * Search things by property value using SPARQL schema search
 * Finds TwinInterfaces that have a specific property, optionally filtered by min/max range.
 *
 * @param {string} property - Property name (e.g., 'temperature')
 * @param {string} operator - Comparison operator ('gt', 'lt', 'eq', 'gte', 'lte', 'ne')
 * @param {number} value - Threshold value
 * @param {string} tenantId - Optional tenant ID filter
 * @returns {Promise<Object>} - Search results with metadata
 */
export async function searchByPropertyValue(property, operator, value, tenantId = null) {
  try {
    const headers = {};
    if (tenantId) {
      headers['X-Tenant-ID'] = tenantId;
    } else {
      // Try to get tenant from localStorage
      try {
        const currentTenantStr = localStorage.getItem("currentTenant");
        if (currentTenantStr) {
          const currentTenant = JSON.parse(currentTenantStr);
          if (currentTenant?.tenant_id) {
            headers['X-Tenant-ID'] = currentTenant.tenant_id;
          }
        }
      } catch (e) {
        // ignore
      }
    }

    const response = await axiosInstance.get('/v2/fuseki/search/property', {
      params: { property, operator, value: value.toString() },
      headers,
    });

    return response.data;

  } catch (error) {
    console.error("Property search error:", error);
    throw error;
  }
}

/**
 * Search things with SPARQL query
 * @param {Object} filters - Filter object
 * @returns {Promise<Array>}
 */
export async function advancedSearch(filters) {
  const { property } = filters;

  const sparqlQuery = `
    PREFIX ts: <http://twin.dtd/ontology#>
    PREFIX tsd: <http://iodt2.com/>

    SELECT ?interface ?name ?propName ?propType ?unit
    WHERE {
      GRAPH ?g {
        ?interface a ts:TwinInterface .
        ?interface ts:name ?name .
        ?interface ts:hasProperty ?prop .
        ?prop ts:propertyName ?propName .
        ?prop ts:propertyType ?propType .
        FILTER(CONTAINS(LCASE(STR(?propName)), "${property.toLowerCase()}"))
        OPTIONAL { ?prop ts:unit ?unit }
      }
    }
    LIMIT 100
  `;

  const response = await axiosInstance.post("/v2/fuseki/sparql/search", {
    query: sparqlQuery,
  });

  return response.data || [];
}

export default {
  searchByPropertyValue,
  advancedSearch,
};
