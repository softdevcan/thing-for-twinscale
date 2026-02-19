import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { ArrowLeft, Download, Trash2, Loader2, FileCode } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import TwinService from '@/services/twinService'

const TwinThingDetails = () => {
  const { interfaceName } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [interfaceData, setInterfaceData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadDetails = async () => {
      setIsLoading(true)
      try {
        const data = await TwinService.getInterfaceDetails(interfaceName)
        setInterfaceData(data)
      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Error',
          description: error.message,
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadDetails()
  }, [interfaceName])

  const handleExport = async () => {
    try {
      const blob = await TwinService.exportAsZip(interfaceName)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${interfaceName}_twin.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Export Error',
        description: error.message,
      })
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${interfaceName}"?`)) {
      return
    }

    try {
      await TwinService.deleteInterface(interfaceName)
      toast({
        title: 'Success',
        description: 'Interface deleted successfully',
      })
      navigate('/things')
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Delete Error',
        description: error.message,
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!interfaceData) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        Interface not found
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/things')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-2xl font-bold">{interfaceData.name}</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export YAML
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {interfaceData.description && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">{interfaceData.description}</p>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="properties">
        <TabsList>
          <TabsTrigger value="properties">
            Properties ({interfaceData.properties?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="relationships">
            Relationships ({interfaceData.relationships?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="commands">
            Commands ({interfaceData.commands?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="dtdl-binding">
            DTDL Binding
          </TabsTrigger>
        </TabsList>

        <TabsContent value="properties">
          <Card>
            <CardHeader>
              <CardTitle>Properties</CardTitle>
            </CardHeader>
            <CardContent>
              {interfaceData.properties?.length > 0 ? (
                <div className="space-y-4">
                  {interfaceData.properties.map((prop, index) => (
                    <div key={index} className="border rounded-md p-4">
                      <div className="flex justify-between">
                        <span className="font-medium">{prop.name}</span>
                        <span className="text-sm text-muted-foreground">
                          {prop.type}
                        </span>
                      </div>
                      {prop.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {prop.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No properties defined</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="relationships">
          <Card>
            <CardHeader>
              <CardTitle>Relationships</CardTitle>
            </CardHeader>
            <CardContent>
              {interfaceData.relationships?.length > 0 ? (
                <div className="space-y-4">
                  {interfaceData.relationships.map((rel, index) => (
                    <div key={index} className="border rounded-md p-4">
                      <div className="flex justify-between">
                        <span className="font-medium">{rel.name}</span>
                        <span className="text-sm text-muted-foreground">
                          → {rel.targetInterface}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No relationships defined</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="commands">
          <Card>
            <CardHeader>
              <CardTitle>Commands</CardTitle>
            </CardHeader>
            <CardContent>
              {interfaceData.commands?.length > 0 ? (
                <div className="space-y-4">
                  {interfaceData.commands.map((cmd, index) => (
                    <div key={index} className="border rounded-md p-4">
                      <span className="font-medium">{cmd.name}</span>
                      {cmd.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {cmd.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No commands defined</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dtdl-binding">
          <Card>
            <CardHeader>
              <CardTitle>DTDL Interface Binding</CardTitle>
            </CardHeader>
            <CardContent>
              {interfaceData.annotations?.['dtdl-interface'] ? (
                <div className="space-y-4">
                  {/* Bound Interface Info */}
                  <div className="border rounded-lg p-4 bg-accent/50">
                    <h4 className="font-semibold text-lg mb-2">
                      {interfaceData.annotations['dtdl-interface-name'] || 'Unknown Interface'}
                    </h4>
                    <p className="text-xs text-muted-foreground font-mono mb-3">
                      {interfaceData.annotations['dtdl-interface']}
                    </p>
                    <div className="flex gap-2">
                      <Badge variant="secondary">
                        {interfaceData.annotations['dtdl-category'] || 'Unknown Category'}
                      </Badge>
                      <Badge variant="outline">
                        {interfaceData.labels?.['thing-type'] || 'device'}
                      </Badge>
                    </div>
                  </div>

                  {/* Property Mapping */}
                  <div>
                    <h5 className="text-sm font-semibold mb-3">Property Mapping</h5>
                    <div className="space-y-2">
                      {interfaceData.properties?.map((prop) => (
                        <div key={prop.name} className="flex items-center justify-between border rounded p-3">
                          <div>
                            <span className="font-medium text-sm">{prop.name}</span>
                            <span className="text-xs text-muted-foreground ml-2">
                              ({prop.type})
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {prop.unit && (
                              <Badge variant="outline" className="text-xs">{prop.unit}</Badge>
                            )}
                            <Badge variant={prop.writable ? "default" : "secondary"} className="text-xs">
                              {prop.writable ? "Writable" : "Read-only"}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <FileCode className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No DTDL interface binding</p>
                  <p className="text-xs mt-2">This Thing was created without a DTDL interface</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default TwinThingDetails
