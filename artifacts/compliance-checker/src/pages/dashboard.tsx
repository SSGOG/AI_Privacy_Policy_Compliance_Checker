import { useState, useRef } from 'react';
import { useLocation } from 'wouter';
import { ShieldCheck, LogOut, Upload, ChevronDown, ChevronUp, Loader2, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { StatusBadge } from '@/components/status-badge';
import { useToast } from '@/hooks/use-toast';
import {
  clearToken,
  analyzeUpload,
  analyzeSample,
  explainClause,
  downloadReport,
  type AnalysisResponse,
  type ClauseResult,
  type ExplainResponse,
} from '@/lib/api';

const LAWS = ['GDPR', 'CCPA'];

const STATUS_EMOJI: Record<string, string> = {
  'Fully Compliant': '✅',
  'Partially Compliant': '⚠️',
  'Non-Compliant': '❌',
  'Not Applicable': '⬜',
};

function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-36 text-slate-600 shrink-0">{label}</span>
      <div className="flex-1 bg-slate-100 rounded-full h-2">
        <div className="h-2 rounded-full" style={{ width: `${value * 100}%`, backgroundColor: color }} />
      </div>
      <span className="w-12 text-right text-slate-700 font-medium">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

function SummaryCard({ law, stats }: { law: string; stats: AnalysisResponse['stats'][string] }) {
  const pct = Math.round(stats.score * 100);
  const color = pct >= 70 ? '#2d9c4e' : pct >= 40 ? '#e07b00' : '#c0392b';
  return (
    <div className="border rounded-lg p-5 text-center" style={{ borderColor: color }}>
      <div className="text-3xl font-bold" style={{ color }}>{pct}%</div>
      <div className="font-semibold mt-1">{law} Compliance Score</div>
      <div className="text-sm text-slate-500 mt-2">
        ✅ {stats.compliant} &nbsp;⚠️ {stats.partial} &nbsp;❌ {stats.non_compliant}
        <br />({stats.total} clauses)
      </div>
    </div>
  );
}

function EvidenceItem({ ev }: { ev: { article: string; title: string; text: string; requirement: string; similarity: number } }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-slate-200 rounded-md overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-2 text-sm text-left bg-slate-50 hover:bg-slate-100"
        onClick={() => setOpen(!open)}
      >
        <span className="font-medium text-[#1e3a5f]">{ev.article}: {ev.title}</span>
        <span className="text-slate-400 ml-2 shrink-0">
          {(ev.similarity * 100).toFixed(0)}% match {open ? <ChevronUp className="inline h-3 w-3" /> : <ChevronDown className="inline h-3 w-3" />}
        </span>
      </button>
      {open && (
        <div className="px-4 py-3 text-sm space-y-2">
          <p className="text-slate-700 italic">"{ev.text}"</p>
          <p className="text-slate-600"><span className="font-medium">Requirement:</span> {ev.requirement}</p>
        </div>
      )}
    </div>
  );
}

function ClauseCard({
  idx,
  clause,
  resultsByLaw,
  laws,
}: {
  idx: number;
  clause: string;
  resultsByLaw: Record<string, ClauseResult[]>;
  laws: string[];
}) {
  const [open, setOpen] = useState(false);
  const [explaining, setExplaining] = useState<string | null>(null);
  const [explanations, setExplanations] = useState<Record<string, ExplainResponse>>({});
  const { toast } = useToast();

  const worstStatus = laws.reduce((worst, law) => {
    const s = resultsByLaw[law]?.[idx]?.status;
    if (s === 'Non-Compliant') return 'Non-Compliant';
    if (s === 'Partially Compliant' && worst !== 'Non-Compliant') return 'Partially Compliant';
    if (s === 'Fully Compliant' && worst === 'Not Applicable') return 'Fully Compliant';
    return worst;
  }, 'Not Applicable' as string);

  const borderColor =
    worstStatus === 'Non-Compliant' ? '#c0392b' :
    worstStatus === 'Partially Compliant' ? '#e07b00' :
    worstStatus === 'Fully Compliant' ? '#2d9c4e' : '#94a3b8';

  async function handleExplain(law: string) {
    const result = resultsByLaw[law]?.[idx];
    if (!result) return;
    setExplaining(law);
    try {
      const exp = await explainClause(clause, law, result);
      setExplanations(prev => ({ ...prev, [law]: exp }));
    } catch (e) {
      toast({ title: 'Explanation failed', description: String(e), variant: 'destructive' });
    } finally {
      setExplaining(null);
    }
  }

  return (
    <div className="border rounded-lg overflow-hidden" style={{ borderLeftWidth: 4, borderLeftColor: borderColor }}>
      <button
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-slate-50"
        onClick={() => setOpen(!open)}
      >
        <span className="font-medium text-sm">
          {STATUS_EMOJI[worstStatus]} Clause {idx + 1} — {clause.slice(0, 90)}{clause.length > 90 ? '…' : ''}
        </span>
        {open ? <ChevronUp className="h-4 w-4 text-slate-400 shrink-0" /> : <ChevronDown className="h-4 w-4 text-slate-400 shrink-0" />}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-4">
          <div className="bg-slate-50 border-l-2 rounded p-3 text-sm text-slate-700" style={{ borderLeftColor: borderColor }}>
            {clause}
          </div>

          <Tabs defaultValue={laws[0]}>
            <TabsList>
              {laws.map(law => (
                <TabsTrigger key={law} value={law}>{law}</TabsTrigger>
              ))}
            </TabsList>
            {laws.map(law => {
              const result = resultsByLaw[law]?.[idx];
              if (!result) return null;
              const exp = explanations[law];
              return (
                <TabsContent key={law} value={law} className="space-y-4 mt-3">
                  <div className="flex flex-wrap gap-4 items-start">
                    <div className="space-y-2 min-w-[180px]">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-slate-500">Status:</span>
                        <StatusBadge status={result.status} />
                      </div>
                      <div className="text-sm text-slate-500">
                        Confidence: <span className="font-medium text-slate-700">{(result.confidence * 100).toFixed(1)}%</span>
                      </div>
                      {result.scores && Object.keys(result.scores).length > 0 && (
                        <div className="space-y-1 pt-1">
                          <ScoreBar label="Fully Compliant" value={result.scores['Fully Compliant'] ?? 0} color="#2d9c4e" />
                          <ScoreBar label="Partially Compliant" value={result.scores['Partially Compliant'] ?? 0} color="#e07b00" />
                          <ScoreBar label="Non-Compliant" value={result.scores['Non-Compliant'] ?? 0} color="#c0392b" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-[200px]">
                      <p className="text-sm font-medium text-slate-700 mb-1">AI Summary</p>
                      <p className="text-sm text-slate-600 bg-blue-50 border border-blue-100 rounded p-3">{result.summary}</p>
                    </div>
                  </div>

                  {result.evidence.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-slate-700">⚖️ Legal Evidence</p>
                      {result.evidence.map((ev, i) => <EvidenceItem key={i} ev={ev} />)}
                    </div>
                  )}

                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">🔬 LIME Explainability</p>
                    {exp ? (
                      <div className="space-y-3">
                        <p className="text-sm text-slate-600 bg-slate-50 border rounded p-3">{exp.textual_summary}</p>
                        {exp.top_features.length > 0 && (
                          <div className="space-y-1">
                            <p className="text-xs text-slate-500 font-medium">Word Impact</p>
                            {exp.top_features.slice(0, 10).map((f, i) => (
                              <div key={i} className="flex items-center gap-2 text-xs">
                                <span className="w-28 truncate text-slate-600">{f.word}</span>
                                <div className="flex-1 flex items-center gap-1">
                                  {f.weight >= 0 ? (
                                    <div className="h-2 rounded" style={{ width: `${Math.min(Math.abs(f.weight) * 300, 100)}%`, backgroundColor: '#2d9c4e' }} />
                                  ) : (
                                    <div className="h-2 rounded" style={{ width: `${Math.min(Math.abs(f.weight) * 300, 100)}%`, backgroundColor: '#c0392b' }} />
                                  )}
                                </div>
                                <span className={`w-14 text-right font-medium ${f.weight >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                                  {f.weight >= 0 ? '+' : ''}{f.weight.toFixed(3)}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                        {exp.highlighted_text && (
                          <div>
                            <p className="text-xs text-slate-500 font-medium mb-1">Highlighted Clause</p>
                            <div className="text-sm leading-7 bg-white border rounded p-3"
                              dangerouslySetInnerHTML={{ __html: exp.highlighted_text }} />
                          </div>
                        )}
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleExplain(law)}
                        disabled={explaining === law}
                        className="border-[#1e3a5f] text-[#1e3a5f] hover:bg-[#1e3a5f] hover:text-white"
                      >
                        {explaining === law ? <><Loader2 className="mr-2 h-3 w-3 animate-spin" />Generating…</> : 'Generate Explanation'}
                      </Button>
                    )}
                  </div>
                </TabsContent>
              );
            })}
          </Tabs>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);

  const [selectedLaws, setSelectedLaws] = useState<string[]>(['GDPR']);
  const [topK, setTopK] = useState(3);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);

  // Sample clause tab
  const [sampleClause, setSampleClause] = useState(
    'We collect your name, email address, and usage data to provide and improve our services. ' +
    'You may request deletion of your personal data at any time by contacting us at privacy@example.com. ' +
    'We retain your data for up to 3 years after account closure and use industry-standard encryption to protect it.'
  );
  const [sampleLoading, setSampleLoading] = useState(false);
  const [sampleResult, setSampleResult] = useState<AnalysisResponse | null>(null);

  function toggleLaw(law: string) {
    setSelectedLaws(prev =>
      prev.includes(law) ? prev.filter(l => l !== law) : [...prev, law]
    );
  }

  function handleLogout() {
    clearToken();
    setLocation('/login');
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!selectedLaws.length) {
      toast({ title: 'Select at least one regulation', variant: 'destructive' });
      return;
    }
    setLoading(true);
    setAnalysis(null);
    try {
      const result = await analyzeUpload(file, selectedLaws, topK);
      setAnalysis(result);
    } catch (err) {
      toast({ title: 'Analysis failed', description: String(err), variant: 'destructive' });
    } finally {
      setLoading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  }

  async function handleSampleAnalyze() {
    if (!selectedLaws.length) {
      toast({ title: 'Select at least one regulation', variant: 'destructive' });
      return;
    }
    setSampleLoading(true);
    setSampleResult(null);
    try {
      const res = await analyzeSample(sampleClause, selectedLaws, topK);
      // Convert sample response to AnalysisResponse shape for reuse
      const resultsByLaw: Record<string, ClauseResult[]> = {};
      const stats: AnalysisResponse['stats'] = {};
      for (const [law, r] of Object.entries(res.results)) {
        resultsByLaw[law] = [r];
        const s = r.status;
        stats[law] = {
          total: 1,
          compliant: s === 'Fully Compliant' ? 1 : 0,
          partial: s === 'Partially Compliant' ? 1 : 0,
          non_compliant: s === 'Non-Compliant' ? 1 : 0,
          irrelevant: s === 'Not Applicable' ? 1 : 0,
          score: s === 'Fully Compliant' ? 1 : s === 'Partially Compliant' ? 0.5 : 0,
        };
      }
      setSampleResult({ policy_name: 'Sample Clause', clauses: [res.clause], results_by_law: resultsByLaw, stats });
    } catch (err) {
      toast({ title: 'Analysis failed', description: String(err), variant: 'destructive' });
    } finally {
      setSampleLoading(false);
    }
  }

  async function handleDownload(format: 'csv' | 'pdf') {
    if (!analysis) return;
    try {
      const blob = await downloadReport(format, {
        policy_name: analysis.policy_name,
        clauses: analysis.clauses,
        results_by_law: analysis.results_by_law,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `compliance_report_${analysis.policy_name}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast({ title: `${format.toUpperCase()} download failed`, description: String(err), variant: 'destructive' });
    }
  }

  const activeAnalysis = analysis;

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-10">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2 text-[#1e3a5f]">
            <ShieldCheck className="h-6 w-6" />
            <span className="font-semibold">AI Privacy Compliance Checker</span>
          </div>
          <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-600 hover:text-[#1e3a5f]">
            <LogOut className="h-4 w-4 mr-1" /> Sign Out
          </Button>
        </div>
      </header>

      <main className="flex-1 mx-auto w-full max-w-6xl px-6 py-8 space-y-8">
        {/* Disclaimer */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-800">
          ⚠️ <strong>Research Tool Disclaimer:</strong> This application is an AI research tool and does <strong>not</strong> constitute legal advice.
          Results should be reviewed by a qualified legal professional before making compliance decisions.
        </div>

        {/* Settings */}
        <Card className="border-slate-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-[#1e3a5f] text-base">Analysis Settings</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-8 items-start">
            <div className="space-y-2">
              <Label className="text-sm font-medium">Regulations</Label>
              <div className="flex gap-3">
                {LAWS.map(law => (
                  <button
                    key={law}
                    onClick={() => toggleLaw(law)}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                      selectedLaws.includes(law)
                        ? 'bg-[#1e3a5f] text-white border-[#1e3a5f]'
                        : 'bg-white text-slate-600 border-slate-300 hover:border-[#1e3a5f]'
                    }`}
                  >
                    {law}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-2 min-w-[200px]">
              <Label className="text-sm font-medium">Evidence articles per clause: <span className="text-[#1e3a5f] font-bold">{topK}</span></Label>
              <Slider
                min={1} max={5} step={1} value={[topK]}
                onValueChange={([v]) => setTopK(v)}
                className="w-48"
              />
            </div>
          </CardContent>
        </Card>

        {/* Main tabs */}
        <Tabs defaultValue="upload">
          <TabsList className="border-b border-slate-200 bg-transparent p-0 h-auto">
            <TabsTrigger value="upload" className="rounded-none border-b-2 border-transparent data-[state=active]:border-[#1e3a5f] data-[state=active]:text-[#1e3a5f] pb-2 mr-4">
              📄 Upload Policy
            </TabsTrigger>
            <TabsTrigger value="sample" className="rounded-none border-b-2 border-transparent data-[state=active]:border-[#1e3a5f] data-[state=active]:text-[#1e3a5f] pb-2">
              📝 Try Sample Clause
            </TabsTrigger>
          </TabsList>

          {/* Upload tab */}
          <TabsContent value="upload" className="mt-6 space-y-6">
            <div className="flex flex-col sm:flex-row gap-4 items-start">
              <div
                className="flex-1 border-2 border-dashed border-slate-300 rounded-lg p-8 text-center cursor-pointer hover:border-[#1e3a5f] transition-colors"
                onClick={() => fileRef.current?.click()}
              >
                <Upload className="h-8 w-8 text-slate-400 mx-auto mb-3" />
                <p className="text-sm font-medium text-slate-700">Click to upload a privacy policy</p>
                <p className="text-xs text-slate-400 mt-1">PDF or TXT — the document will be split into clauses for analysis</p>
                <input ref={fileRef} type="file" accept=".pdf,.txt" className="hidden" onChange={handleFileUpload} />
              </div>
              <div className="text-sm text-slate-500 space-y-1 pt-2">
                <p className="font-medium text-slate-700">Supported formats</p>
                <p>• PDF (privacy policy documents)</p>
                <p>• TXT (plain text)</p>
                <p className="mt-2 text-xs">For best results, upload the full policy text.</p>
              </div>
            </div>

            {loading && (
              <div className="flex items-center gap-3 text-[#1e3a5f] py-4">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Analysing document…</span>
              </div>
            )}

            {activeAnalysis && (
              <AnalysisResults
                analysis={activeAnalysis}
                laws={selectedLaws}
                onDownload={handleDownload}
              />
            )}

            {!activeAnalysis && !loading && (
              <GettingStarted />
            )}
          </TabsContent>

          {/* Sample clause tab */}
          <TabsContent value="sample" className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label>Paste a policy clause to test</Label>
              <Textarea
                value={sampleClause}
                onChange={e => setSampleClause(e.target.value)}
                rows={5}
                className="resize-none border-slate-300 focus:border-[#1e3a5f]"
              />
            </div>
            <Button
              onClick={handleSampleAnalyze}
              disabled={sampleLoading || !sampleClause.trim()}
              className="bg-[#1e3a5f] hover:bg-[#152a45] text-white"
            >
              {sampleLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analysing…</> : '🔍 Analyse Clause'}
            </Button>

            {sampleResult && (
              <AnalysisResults analysis={sampleResult} laws={selectedLaws} />
            )}
          </TabsContent>
        </Tabs>
      </main>

      <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        AI Privacy Compliance Checker — Research Tool | Not legal advice. For informational purposes only.
      </footer>
    </div>
  );
}

function AnalysisResults({
  analysis,
  laws,
  onDownload,
}: {
  analysis: AnalysisResponse;
  laws: string[];
  onDownload?: (format: 'csv' | 'pdf') => void;
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-[#1e3a5f]">
          📊 Results — <span className="font-normal text-slate-600">{analysis.policy_name}</span>
          <span className="ml-2 text-sm text-slate-400">({analysis.clauses.length} clauses)</span>
        </h2>
        {onDownload && (
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => onDownload('csv')} className="border-[#1e3a5f] text-[#1e3a5f] hover:bg-[#1e3a5f] hover:text-white">
              <Download className="h-3 w-3 mr-1" /> CSV
            </Button>
            <Button size="sm" variant="outline" onClick={() => onDownload('pdf')} className="border-[#1e3a5f] text-[#1e3a5f] hover:bg-[#1e3a5f] hover:text-white">
              <Download className="h-3 w-3 mr-1" /> PDF
            </Button>
          </div>
        )}
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {Object.entries(analysis.stats).map(([law, stats]) => (
          <SummaryCard key={law} law={law} stats={stats} />
        ))}
      </div>

      {/* Clause list */}
      <div className="space-y-3">
        <h3 className="font-semibold text-[#1e3a5f]">🔍 Clause-by-Clause Analysis</h3>
        {analysis.clauses.map((clause, idx) => (
          <ClauseCard
            key={idx}
            idx={idx}
            clause={clause}
            resultsByLaw={analysis.results_by_law}
            laws={laws.filter(l => analysis.results_by_law[l])}
          />
        ))}
      </div>
    </div>
  );
}

function GettingStarted() {
  return (
    <div className="grid sm:grid-cols-2 gap-6 pt-2">
      <Card className="border-slate-200">
        <CardHeader><CardTitle className="text-[#1e3a5f] text-sm">How it works</CardTitle></CardHeader>
        <CardContent className="text-sm text-slate-600 space-y-2">
          <p>1. <strong>Upload</strong> your privacy policy PDF or TXT</p>
          <p>2. <strong>Select</strong> regulations to check (GDPR, CCPA)</p>
          <p>3. <strong>Analyse</strong> — the AI segments clauses, classifies each using NLI, retrieves legal evidence via RAG, and explains decisions with LIME</p>
          <p>4. <strong>Download</strong> the full compliance report</p>
        </CardContent>
      </Card>
      <Card className="border-slate-200">
        <CardHeader><CardTitle className="text-[#1e3a5f] text-sm">What the system checks</CardTitle></CardHeader>
        <CardContent className="text-sm text-slate-600 space-y-3">
          <div>
            <p className="font-medium text-slate-700">GDPR</p>
            <p>Lawfulness, transparency, purpose limitation, data minimisation, storage limits, user rights, security, breach notification, international transfers</p>
          </div>
          <div>
            <p className="font-medium text-slate-700">CCPA</p>
            <p>Right to know, delete, correct, opt-out of data sales, sensitive data disclosures, non-discrimination, consumer request procedures</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
