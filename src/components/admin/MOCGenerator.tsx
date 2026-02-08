import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Download, Sparkles, AlertCircle } from 'lucide-react';

/**
 * MOC Generator Component for Admin Dashboard
 * DNA-Conditioned LEGO MOC generation with physics validation
 */
export default function MOCGenerator() {
    const [theme, setTheme] = useState('star-wars');
    const [category, setCategory] = useState('small_ship');
    const [maxParts, setMaxParts] = useState(25);
    const [usePhysics, setUsePhysics] = useState(true);
    const [useDNA, setUseDNA] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [result, setResult] = useState(null);

    const handleGenerate = async () => {
        setGenerating(true);
        setResult(null);

        try {
            const response = await fetch('/api/generate-moc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    theme_id: theme === 'star-wars' ? 158 : null,
                    category,
                    max_parts: maxParts,
                    use_physics: usePhysics,
                    use_dna: useDNA
                })
            });

            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('Generation failed:', error);
            setResult({ error: error.message });
        } finally {
            setGenerating(false);
        }
    };

    const downloadFile = (content, filename, format) => {
        const blob = new Blob([content], { type: format === 'io' ? 'application/json' : 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Sparkles className="h-5 w-5" />
                        DNA-Conditioned MOC Generator
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Configuration Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="theme">Theme</Label>
                            <Select value={theme} onValueChange={setTheme}>
                                <SelectTrigger id="theme">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="star-wars">Star Wars</SelectItem>
                                    <SelectItem value="city" disabled>City (Coming Soon)</SelectItem>
                                    <SelectItem value="technic" disabled>Technic (Coming Soon)</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="category">Category</Label>
                            <Select value={category} onValueChange={setCategory}>
                                <SelectTrigger id="category">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="small_ship">Small Ship</SelectItem>
                                    <SelectItem value="medium_ship">Medium Ship</SelectItem>
                                    <SelectItem value="vehicle">Vehicle</SelectItem>
                                    <SelectItem value="building">Building</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="maxParts">Max Parts: {maxParts}</Label>
                            <Input
                                id="maxParts"
                                type="range"
                                min="10"
                                max="100"
                                step="5"
                                value={maxParts}
                                onChange={(e) => setMaxParts(parseInt(e.target.value))}
                            />
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="useDNA">DNA Conditioning</Label>
                                <Switch id="useDNA" checked={useDNA} onCheckedChange={setUseDNA} />
                            </div>
                            <div className="flex items-center justify-between">
                                <Label htmlFor="usePhysics">Physics Validation</Label>
                                <Switch id="usePhysics" checked={usePhysics} onCheckedChange={setUsePhysics} />
                            </div>
                        </div>
                    </div>

                    {/* Generate Button */}
                    <Button
                        onClick={handleGenerate}
                        disabled={generating}
                        className="w-full"
                        size="lg"
                    >
                        {generating ? (
                            <>
                                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Sparkles className="mr-2 h-4 w-4" />
                                Generate MOC
                            </>
                        )}
                    </Button>

                    {/* Results Section */}
                    {result && (
                        <div className="mt-6 space-y-4">
                            {result.error ? (
                                <div className="flex items-start gap-2 rounded-lg bg-red-50 p-4 text-red-800">
                                    <AlertCircle className="h-5 w-5 mt-0.5" />
                                    <div>
                                        <p className="font-medium">Generation Failed</p>
                                        <p className="text-sm">{result.error}</p>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="rounded-lg bg-green-50 p-4">
                                        <h3 className="font-medium text-green-900 mb-2">✅ MOC Generated Successfully!</h3>
                                        <div className="grid grid-cols-2 gap-2 text-sm text-green-800">
                                            <div>Parts: {result.num_parts}</div>
                                            <div>SNOT Ratio: {(result.snot_ratio * 100).toFixed(1)}%</div>
                                            <div>Complexity: {result.complexity?.toFixed(2)}</div>
                                            <div>Stability: {result.stability_score?.toFixed(2)}/1.00</div>
                                        </div>
                                    </div>

                                    {/* Download Buttons */}
                                    <div className="grid grid-cols-2 gap-3">
                                        <Button
                                            variant="outline"
                                            onClick={() => downloadFile(result.io_content, 'generated_moc.io', 'io')}
                                        >
                                            <Download className="mr-2 h-4 w-4" />
                                            Download .io (Studio)
                                        </Button>
                                        <Button
                                            variant="outline"
                                            onClick={() => downloadFile(result.ldr_content, 'generated_moc.ldr', 'ldr')}
                                        >
                                            <Download className="mr-2 h-4 w-4" />
                                            Download .ldr (LDraw)
                                        </Button>
                                    </div>

                                    {/* DNA Match Info */}
                                    {useDNA && result.dna_match && (
                                        <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                                            <p className="font-medium">DNA Matching:</p>
                                            <p>Color Consistency: {(result.dna_match.color_consistency * 100).toFixed(0)}%</p>
                                            <p>SNOT Target: {(result.dna_match.snot_target * 100).toFixed(1)}%</p>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    )}

                    {/* Info Section */}
                    <div className="border-t pt-4 text-sm text-gray-600">
                        <p className="font-medium mb-2">System Status:</p>
                        <ul className="space-y-1">
                            <li>✅ Module 1: ID Cross-Reference</li>
                            <li>✅ Module 2: DNA Extraction ({theme === 'star-wars' ? '23 sets' : '0 sets'})</li>
                            <li>⚙️ Module 3: Enhanced GNN (Training data expanded)</li>
                            <li>✅ Module 4: Physics Validation</li>
                            <li>✅ Module 5: Studio Export</li>
                        </ul>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
