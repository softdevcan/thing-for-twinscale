/**
 * DTDL Validation Panel Component
 *
 * Displays real-time DTDL validation results while user creates Thing.
 * Shows compatibility score, matched/missing fields, and validation issues.
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, AlertTriangle, Info } from 'lucide-react'
import { validateThing } from '@/api/dtdl'

const DTDLValidationPanel = ({ formData, dtdlInterface }) => {
  const [validationResult, setValidationResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!dtdlInterface || !formData.properties.length) {
      setValidationResult(null)
      return
    }

    // Debounced validation (500ms delay)
    const timer = setTimeout(async () => {
      setLoading(true)
      try {
        // Convert properties array to dictionary format expected by backend
        // Send typed scalar values so backend schema validation works correctly
        const propertiesDict = {}
        const telemetryDict = {}

        formData.properties.forEach(prop => {
          const defaultValue = prop.type === 'boolean' ? false
            : ['integer', 'long'].includes(prop.type) ? 0
            : ['float', 'double'].includes(prop.type) ? 0.1
            : ''

          if (prop.isTelemetry) {
            telemetryDict[prop.name] = defaultValue
          } else {
            propertiesDict[prop.name] = defaultValue
          }
        })

        const result = await validateThing({
          thing_data: {
            properties: propertiesDict,
            telemetry: telemetryDict
          },
          dtmi: dtdlInterface.dtmi,
          strict: false
        })
        setValidationResult(result)
      } catch (error) {
        console.error('Validation failed:', error)
        // Set null result to hide validation panel on error
        setValidationResult(null)
      } finally {
        setLoading(false)
      }
    }, 500)

    return () => clearTimeout(timer)
  }, [formData.properties, formData.commands, dtdlInterface])

  if (!dtdlInterface) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Info className="h-4 w-4" />
          DTDL Compliance
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            Validating...
          </div>
        )}

        {validationResult && !loading && (
          <div className="space-y-4">
            {/* Compatibility Score */}
            <div className="flex items-center justify-between p-3 bg-accent/50 rounded-lg">
              <span className="text-sm font-medium">Compatibility Score</span>
              <Badge variant={validationResult.is_compatible ? "default" : "destructive"} className="text-sm">
                {validationResult.compatibility_score}/100
              </Badge>
            </div>

            {/* Matched Properties */}
            {validationResult.matched_properties?.length > 0 && (
              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-green-600 mb-2">
                  <CheckCircle className="h-4 w-4" />
                  Matched Properties ({validationResult.matched_properties.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {validationResult.matched_properties.map((prop) => (
                    <Badge key={prop} variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                      {prop}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Matched Telemetry */}
            {validationResult.matched_telemetry?.length > 0 && (
              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-blue-600 mb-2">
                  <CheckCircle className="h-4 w-4" />
                  Matched Telemetry ({validationResult.matched_telemetry.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {validationResult.matched_telemetry.map((tel) => (
                    <Badge key={tel} variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100">
                      {tel}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Properties */}
            {validationResult.missing_properties?.length > 0 && (
              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-orange-600 mb-2">
                  <AlertTriangle className="h-4 w-4" />
                  Missing Properties ({validationResult.missing_properties.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {validationResult.missing_properties.map((prop) => (
                    <Badge key={prop} variant="outline" className="border-orange-400 text-orange-600">
                      {prop}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Telemetry */}
            {validationResult.missing_telemetry?.length > 0 && (
              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-orange-600 mb-2">
                  <AlertTriangle className="h-4 w-4" />
                  Missing Telemetry ({validationResult.missing_telemetry.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {validationResult.missing_telemetry.map((tel) => (
                    <Badge key={tel} variant="outline" className="border-orange-400 text-orange-600">
                      {tel}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Validation Issues */}
            {validationResult.issues?.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm font-medium">Validation Issues:</div>
                {validationResult.issues.slice(0, 3).map((issue, idx) => (
                  <Alert key={idx} variant={issue.severity === 'ERROR' ? 'destructive' : 'default'}>
                    <AlertDescription className="text-xs">
                      <strong>{issue.field}:</strong> {issue.message}
                      {issue.suggestion && (
                        <div className="mt-1 text-muted-foreground italic">{issue.suggestion}</div>
                      )}
                    </AlertDescription>
                  </Alert>
                ))}
                {validationResult.issues.length > 3 && (
                  <p className="text-xs text-muted-foreground">
                    ... and {validationResult.issues.length - 3} more issue(s)
                  </p>
                )}
              </div>
            )}

            {/* No Issues */}
            {validationResult.is_compatible && validationResult.issues?.length === 0 && (
              <div className="flex items-center gap-2 text-sm text-green-600 p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <CheckCircle className="h-4 w-4" />
                Thing is fully compatible with selected DTDL interface
              </div>
            )}
          </div>
        )}

        {!validationResult && !loading && formData.properties.length === 0 && (
          <div className="text-center py-6 text-muted-foreground text-sm">
            <Info className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Add properties to see validation results</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default DTDLValidationPanel
