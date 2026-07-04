import { Link } from 'wouter';
import { Button } from '@/components/ui/button';
import { ShieldCheck, FileSearch, Scale, FileText } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <header className="border-b border-slate-200">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2 text-[#1e3a5f]">
            <ShieldCheck className="h-7 w-7" />
            <span className="font-semibold">AI Privacy Compliance Checker</span>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/signup">
              <Button variant="outline" className="border-[#1e3a5f] text-[#1e3a5f] hover:bg-[#1e3a5f] hover:text-white">Sign Up</Button>
            </Link>
            <Link href="/login">
              <Button className="bg-[#1e3a5f] hover:bg-[#152a45] text-white">Sign In</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-16">
        <div className="max-w-3xl text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-[#1e3a5f] tracking-tight">
            AI Privacy Compliance Checker
          </h1>
          <p className="mt-6 text-lg md:text-xl text-slate-700 leading-relaxed">
            Your intelligent assistant for GDPR &amp; CCPA data protection compliance
          </p>
          <p className="mt-4 text-slate-500 max-w-2xl mx-auto">
            Upload privacy policies, analyse clause-by-clause compliance, retrieve legal evidence,
            and generate detailed reports — powered by local AI models.
          </p>
          <div className="mt-10">
            <Link href="/login">
              <Button size="lg" className="bg-[#1e3a5f] hover:bg-[#152a45] text-white px-10">
                Get Started
              </Button>
            </Link>
          </div>
        </div>

        <div className="mt-20 grid sm:grid-cols-3 gap-6 max-w-4xl w-full">
          {[
            { icon: FileSearch, title: 'Clause-Level Analysis', desc: 'Every clause of your privacy policy is individually classified against GDPR and CCPA requirements.' },
            { icon: Scale, title: 'Legal Evidence Retrieval', desc: 'Relevant legal articles are retrieved from a built-in knowledge base using semantic search.' },
            { icon: FileText, title: 'Explainable AI', desc: 'LIME explanations show exactly which words drove each compliance decision.' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="border border-slate-200 rounded-lg p-6 text-left">
              <Icon className="h-6 w-6 text-[#1e3a5f] mb-3" />
              <h3 className="font-semibold text-slate-800 mb-2">{title}</h3>
              <p className="text-sm text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-sm text-slate-400">
        Research tool — not legal advice. Results should be reviewed by a qualified legal professional.
      </footer>
    </div>
  );
}
