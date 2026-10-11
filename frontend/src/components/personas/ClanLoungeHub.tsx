import React, { useState, useEffect, useRef } from 'react';
import { Shield, Send } from 'lucide-react';
import { MatchInfo, ClanInfo, ClanChatMessage, UserProfile } from '../../types';
import { soundSynth } from '../../services/audioSynth';

interface ClanLoungeHubProps {
  match: MatchInfo;
  user: UserProfile;
  clans: ClanInfo[];
}

export const ClanLoungeHub: React.FC<ClanLoungeHubProps> = ({
  user,
  clans
}) => {
  const [messages, setMessages] = useState<ClanChatMessage[]>([
    { id: '1', clanId: 'clan_mumbai_army', userId: 'u_1', username: 'SuperNova99', message: 'Kohli looks in insane touch today! 🚀', timestamp: '20:42', badge: 'MVP' },
    { id: '2', clanId: 'clan_mumbai_army', userId: 'u_2', username: 'PaltanChief', message: 'Everyone vote boundary on 17.5 for clan XP! 🔥', timestamp: '20:43', badge: 'CAPTAIN' },
    { id: '3', clanId: 'clan_mumbai_army', userId: 'u_3', username: 'VortexFan', message: 'Starc bowling around the wicket, watch yorker', timestamp: '20:43' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const activeClan = clans.find((c) => c.id === user.clanId) || clans[0];
  const rivalClan = clans.find((c) => c.id !== user.clanId) || clans[1];

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    soundSynth.playCoinChime();
    const newMsg: ClanChatMessage = {
      id: `msg_${Date.now()}`,
      clanId: activeClan.id,
      userId: user.userId,
      username: user.username,
      message: inputMessage.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      badge: 'PRO'
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputMessage('');
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="space-y-3 animate-fade-in">
      
      {/* Clan War Battle Header */}
      <div className="glass-panel p-3.5 border border-amber-500/40 shadow-[0_0_25px_rgba(255,183,3,0.12)]">
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30">
              <Shield className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <h4 className="text-xs font-display font-bold text-white">
                Clan Watch Lounge & Battle
              </h4>
              <p className="text-[10px] text-amber-300/80 font-mono">
                Combined Score War • +15% XP Boost
              </p>
            </div>
          </div>

          <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono font-bold">
            WAR ACTIVE
          </span>
        </div>

        {/* Territory Progress Bar */}
        <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 mb-2.5">
          <div className="flex items-center justify-between text-[11px] font-mono font-bold mb-1">
            <span className="text-amber-400 flex items-center gap-1">
              <span>{activeClan.badge}</span> {activeClan.name.split(' ')[0]} ({activeClan.totalXp.toLocaleString()} XP)
            </span>
            <span className="text-rose-400 flex items-center gap-1">
              {rivalClan.name.split(' ')[0]} <span>{rivalClan.badge}</span>
            </span>
          </div>

          <div className="w-full h-1.5 rounded-full bg-rose-950 overflow-hidden flex">
            <div 
              className="h-full bg-amber-400 transition-all duration-500 shadow-[0_0_8px_#ffb703]" 
              style={{ width: '58%' }} 
            />
          </div>
          <div className="flex justify-between text-[9px] text-slate-400 font-mono mt-1">
            <span>58% Territory Controlled</span>
            <span>Rally Bonus Active</span>
          </div>
        </div>

        {/* Live Chat Stream */}
        <div className="p-2.5 rounded-xl bg-black/50 border border-white/5 h-36 overflow-y-auto space-y-1.5 mb-2.5">
          {messages.map((m) => (
            <div key={m.id} className="text-xs">
              <div className="flex items-center gap-1">
                <span className="font-display font-bold text-amber-300 text-[11px]">{m.username}</span>
                {m.badge && (
                  <span className="text-[8px] px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 font-mono font-bold">
                    {m.badge}
                  </span>
                )}
                <span className="text-[9px] text-slate-500 font-mono ml-auto">{m.timestamp}</span>
              </div>
              <p className="text-slate-200 text-[11px] pl-1 border-l border-amber-500/30">
                {m.message}
              </p>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Send Box */}
        <form onSubmit={handleSendMessage} className="flex gap-1.5">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder={`Message ${activeClan.name}...`}
            className="flex-1 px-2.5 py-1.5 rounded-lg bg-black/60 border border-white/10 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-amber-400"
          />
          <button
            type="submit"
            className="px-3 py-1.5 rounded-lg btn-primary-gold text-xs font-bold font-display flex items-center gap-1 cursor-pointer"
          >
            <Send className="w-3 h-3" />
            <span>Send</span>
          </button>
        </form>

      </div>

    </div>
  );
};
