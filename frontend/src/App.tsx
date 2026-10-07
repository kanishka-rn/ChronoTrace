import { useState } from 'react';
import { BlueMeshyBackground } from '@/components/ui/blue-meshy-background';
import {
  Video,
  MessageSquare,
  Clock,
  Users,
  Box,
  AlertTriangle,
  Activity,
  Play,
  Upload,
  Link,
  Search
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('video');
  const [url, setUrl] = useState('');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState<any>(null);

  const analyzeUrl = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/video/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const result = await res.json();
      if (result.analysis_id) {
        setAnalysisId(result.analysis_id);
        fetchData(result.analysis_id);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const fetchData = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/analysis/${id}`);
      const result = await res.json();
      setData(result);
      setActiveTab('dashboard');
    } catch (e) {
      console.error(e);
    }
  };

  const handleQuery = async () => {
    if (!analysisId || !query) return;
    try {
      const res = await fetch(`http://localhost:8000/api/analysis/${analysisId}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, timestamp: 0.0 })
      });
      const result = await res.json();
      setQueryResult(result);
    } catch (e) {
      console.error(e);
    }
  };

  const navItems = [
    { id: 'video', label: 'Video Input', icon: Video },
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'ask', label: 'Ask Video', icon: MessageSquare },
    { id: 'timeline', label: 'Timeline', icon: Clock },
    { id: 'tracks', label: 'People / Tracks', icon: Users },
  ];

  return (
    <BlueMeshyBackground>
      <div className="flex h-16 items-center justify-between border-b border-slate-800 px-6 bg-slate-950/50 backdrop-blur">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-cyan-500 flex items-center justify-center font-bold">CT</div>
          <div>
            <h1 className="font-bold text-lg leading-tight text-white">CHRONOTRACE AI</h1>
            <p className="text-xs text-slate-400">Evidence-Grounded Temporal Video Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-cyan-400 font-medium">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
          </span>
          {loading ? 'ANALYZING' : (analysisId ? 'ONLINE' : 'READY')}
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* SIDEBAR */}
        <div className="w-64 border-r border-slate-800 bg-slate-950/50 p-4 flex flex-col gap-2">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-colors ${
                activeTab === item.id ? 'bg-cyan-950 text-cyan-400 border border-cyan-800/50' : 'text-slate-400 hover:text-white hover:bg-slate-900'
              }`}
            >
              <item.icon size={18} />
              {item.label}
            </button>
          ))}
        </div>

        {/* MAIN CONTENT */}
        <div className="flex-1 overflow-y-auto p-8">
          {activeTab === 'video' && (
            <div className="max-w-2xl mx-auto mt-12 bg-slate-900 border border-slate-800 p-8 rounded-xl">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Video className="text-cyan-400" /> Video Input
              </h2>
              
              <div className="flex gap-4 mb-6">
                <button className="flex-1 py-3 bg-slate-800 rounded-md text-sm font-medium text-white hover:bg-slate-700 transition flex items-center justify-center gap-2 border border-slate-700">
                  <Upload size={16} /> Upload Video
                </button>
                <button className="flex-1 py-3 bg-cyan-950 text-cyan-400 rounded-md text-sm font-medium border border-cyan-800 transition flex items-center justify-center gap-2">
                  <Link size={16} /> YouTube / IG
                </button>
              </div>

              <div className="space-y-4">
                <label className="text-sm font-medium text-slate-300">Paste Video URL</label>
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://youtube.com/..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-3 text-white focus:outline-none focus:border-cyan-500"
                />
                
                <button
                  onClick={analyzeUrl}
                  disabled={loading || !url}
                  className="w-full py-4 mt-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-md font-bold transition disabled:opacity-50"
                >
                  {loading ? 'ANALYZING VIDEO...' : 'ANALYZE VIDEO'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'dashboard' && data && (
            <div className="max-w-6xl mx-auto space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* VIDEO QUALITY */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                  <h3 className="text-sm font-medium text-slate-400 mb-4 uppercase tracking-wider">Video Quality</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span className="text-slate-400">Resolution</span><span className="text-white font-medium">{data.metadata.resolution.join(' × ')}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">FPS</span><span className="text-white font-medium">{data.metadata.fps}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Quality</span><span className="text-cyan-400 font-bold">{data.quality.overall_category}</span></div>
                  </div>
                </div>

                {/* CONFIDENCE */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                  <h3 className="text-sm font-medium text-slate-400 mb-4 uppercase tracking-wider">Analysis Confidence</h3>
                  <div className="text-4xl font-bold text-cyan-400 mb-2">{(data.confidence.overall * 100).toFixed(0)}%</div>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between"><span className="text-slate-500">Detection</span><span className="text-slate-300">{(data.confidence.detection * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Tracking</span><span className="text-slate-300">{(data.confidence.tracking * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Events</span><span className="text-slate-300">{(data.confidence.event * 100).toFixed(0)}%</span></div>
                  </div>
                </div>
                
                {/* METRICS */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl col-span-2 flex items-center justify-around">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">{data.stats.tracksCount}</div>
                    <div className="text-xs text-slate-400 uppercase mt-1">Tracks</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">{data.stats.eventsCount}</div>
                    <div className="text-xs text-slate-400 uppercase mt-1">Events</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">{data.stats.relationsCount}</div>
                    <div className="text-xs text-slate-400 uppercase mt-1">Relations</div>
                  </div>
                </div>
              </div>
              
              {/* CURRENT SCENE */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                <h3 className="text-sm font-medium text-slate-400 mb-6 uppercase tracking-wider">Current Scene Overview</h3>
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-slate-950 p-4 rounded-lg flex items-center gap-4">
                    <div className="p-3 bg-blue-900/30 text-blue-400 rounded-lg"><Users size={24} /></div>
                    <div><div className="text-2xl font-bold text-white">7</div><div className="text-xs text-slate-500">People</div></div>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-lg flex items-center gap-4">
                    <div className="p-3 bg-emerald-900/30 text-emerald-400 rounded-lg"><Activity size={24} /></div>
                    <div><div className="text-2xl font-bold text-white">5</div><div className="text-xs text-slate-500">Moving</div></div>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-lg flex items-center gap-4">
                    <div className="p-3 bg-rose-900/30 text-rose-400 rounded-lg"><AlertTriangle size={24} /></div>
                    <div><div className="text-2xl font-bold text-white">2</div><div className="text-xs text-slate-500">Stationary</div></div>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-lg flex items-center gap-4">
                    <div className="p-3 bg-indigo-900/30 text-indigo-400 rounded-lg"><Box size={24} /></div>
                    <div><div className="text-2xl font-bold text-white">18</div><div className="text-xs text-slate-500">Objects</div></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ask' && (
            <div className="max-w-3xl mx-auto mt-8">
              <h2 className="text-2xl font-bold text-white mb-6">Ask the Video</h2>
              <div className="flex gap-2 mb-8">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. What happened before Person #3 exited?"
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-md p-4 text-white focus:outline-none focus:border-cyan-500"
                />
                <button
                  onClick={handleQuery}
                  className="px-6 bg-cyan-600 hover:bg-cyan-500 text-white rounded-md font-bold transition flex items-center gap-2"
                >
                  <Search size={18} /> Ask
                </button>
              </div>

              {queryResult && (
                <div className="bg-slate-900 border border-cyan-900/50 p-6 rounded-xl">
                  <div className="text-xs text-cyan-500 font-bold tracking-wider mb-2 uppercase">ANSWER</div>
                  <div className="text-lg text-white mb-6">{queryResult.answer || "Insufficient evidence to answer this question."}</div>
                  
                  {queryResult.answer_events && queryResult.answer_events.length > 0 && (
                    <div className="border-t border-slate-800 pt-6">
                      <div className="text-xs text-slate-400 font-bold tracking-wider mb-4 uppercase">Reasoning Chain</div>
                      <div className="space-y-3">
                        {queryResult.answer_events.map((e: any, idx: number) => (
                          <div key={idx} className="flex flex-col">
                            <div className="flex items-center gap-4 bg-slate-950 p-3 rounded-md">
                              <div className="font-mono text-cyan-400 text-sm">{e.start.toFixed(1)}s</div>
                              <div className="font-bold text-slate-200">{e.type}</div>
                              <div className="text-slate-500 text-sm">Track {e.track_id}</div>
                            </div>
                            {idx < queryResult.answer_events.length - 1 && (
                              <div className="w-px h-4 bg-slate-700 ml-8 my-1"></div>
                            )}
                          </div>
                        ))}
                      </div>
                      
                      <div className="mt-8 flex justify-between items-center bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <div>
                          <div className="text-xs text-slate-500">Evidence Strength</div>
                          <div className="text-lg font-bold text-cyan-400">{(queryResult.confidence * 100).toFixed(0)}%</div>
                        </div>
                        <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded font-medium transition">
                          <Play size={16} /> Play Evidence Clip
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {/* Default state if no data but tabs selected */}
          {activeTab !== 'video' && !data && (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Search size={48} className="mb-4 opacity-20" />
              <p>Upload a video to view {activeTab} data.</p>
            </div>
          )}
        </div>
      </div>
    </BlueMeshyBackground>
  );
}
