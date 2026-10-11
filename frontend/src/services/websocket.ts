import { MatchTelemetry, ContextualPrediction, CrowdDecibelSnapshot, ClanChatMessage } from '../types';

type MessageHandler = (data: any) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private subscribers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectTimer: any = null;
  private simulationTimer: any = null;
  private isConnected: boolean = false;
  private activeMatchId: string = 'IND_AUS_T20_2026';

  constructor() {
    this.connect();
  }

  public connect() {
    if (typeof window === 'undefined') return;

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.stopSimulation();
        this.dispatch('CONNECTION_STATUS', { connected: true });
        
        // Subscribe to active match channels
        this.subscribeMatch(this.activeMatchId);
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          this.dispatch(msg.type, msg.data || msg);
        } catch (e) {
          console.warn('WS JSON parse error', e);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.dispatch('CONNECTION_STATUS', { connected: false });
        this.startSimulation(); // Fallback simulation engine
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.isConnected = false;
        this.startSimulation();
      };
    } catch (e) {
      this.startSimulation();
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (!this.isConnected) {
        this.connect();
      }
    }, 4000);
  }

  public subscribeMatch(matchId: string) {
    this.activeMatchId = matchId;
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'SUBSCRIBE', channel: `telemetry:${matchId}` }));
      this.ws.send(JSON.stringify({ action: 'SUBSCRIBE', channel: `predictions:${matchId}` }));
      this.ws.send(JSON.stringify({ action: 'SUBSCRIBE', channel: `crowd:${matchId}` }));
    }
  }

  public sendCheer(matchId: string, intensity: number = 1.0) {
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'CHEER', matchId, intensity }));
    } else {
      // Local simulated response
      const snap: CrowdDecibelSnapshot = {
        matchId,
        currentDecibels: Math.min(122, Math.round(94 + Math.random() * 24 * intensity)),
        peakDecibels: 118.8,
        cheerCountTotal: 48290 + Math.floor(Math.random() * 20),
        hypeLevel: intensity > 1.4 ? 'ROARING' : 'HYPED',
        vibeHapticThreshold: true
      };
      this.dispatch('CROWD_DECIBELS', snap);
    }
  }

  public sendVote(matchId: string, predictionId: string, selectedOption: string, stakeTokens: number) {
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'VOTE',
        matchId,
        predictionId,
        selectedOption,
        stakeTokens
      }));
    }
  }

  public on(event: string, handler: MessageHandler) {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    this.subscribers.get(event)!.add(handler);
    return () => this.off(event, handler);
  }

  public off(event: string, handler: MessageHandler) {
    if (this.subscribers.has(event)) {
      this.subscribers.get(event)!.delete(handler);
    }
  }

  private dispatch(event: string, data: any) {
    if (this.subscribers.has(event)) {
      this.subscribers.get(event)!.forEach(fn => fn(data));
    }
    if (this.subscribers.has('*')) {
      this.subscribers.get('*')!.forEach(fn => fn({ event, data }));
    }
  }

  // Fallback High-Fidelity Simulation Stream
  private startSimulation() {
    if (this.simulationTimer) return;

    let frameCount = 0;
    this.simulationTimer = setInterval(() => {
      frameCount++;
      const now = Date.now();

      // 1. Simulated Telemetry Feed
      const isCricket = this.activeMatchId.includes('IND_AUS') || this.activeMatchId.includes('T20');
      const isFootball = this.activeMatchId.includes('MCI_RMA') || this.activeMatchId.includes('UCL');

      const telemetry: MatchTelemetry = {
        matchId: this.activeMatchId,
        sport: isCricket ? 'CRICKET' : isFootball ? 'FOOTBALL' : 'BASKETBALL',
        timestampMs: now,
        ball: {
          x: Math.sin(frameCount * 0.1) * 35 + 50,
          y: Math.cos(frameCount * 0.12) * 25 + 50,
          z: Math.abs(Math.sin(frameCount * 0.2)) * 8,
          speedKmh: isCricket 
            ? Math.round(136 + Math.random() * 12) 
            : isFootball 
            ? Math.round(72 + Math.random() * 38)
            : Math.round(32 + Math.random() * 16),
          trajectoryAngle: Math.round(28 + Math.random() * 14),
          spinRpm: 2400 + Math.floor(Math.random() * 400)
        },
        players: [
          { id: 'p1', name: isCricket ? 'V. Kohli' : isFootball ? 'K. De Bruyne' : 'L. James', team: 'home', x: 48 + Math.sin(frameCount * 0.08) * 15, y: 52 + Math.cos(frameCount * 0.08) * 10, speedKmh: 24.5, role: 'Key Attacker' },
          { id: 'p2', name: isCricket ? 'M. Starc' : isFootball ? 'E. Haaland' : 'S. Curry', team: 'away', x: 54 + Math.sin(frameCount * 0.1) * 12, y: 46 + Math.cos(frameCount * 0.1) * 8, speedKmh: 31.8, role: 'Pace Striker' },
          { id: 'p3', name: isCricket ? 'H. Pandya' : isFootball ? 'Vinicius Jr' : 'A. Davis', team: 'home', x: 62 + Math.sin(frameCount * 0.05) * 8, y: 58 + Math.cos(frameCount * 0.05) * 6, speedKmh: 28.2, role: 'Clutch All-Rounder' },
        ],
        tacticalAnalysis: {
          expectedMetricLabel: isCricket ? 'xWicket' : isFootball ? 'xG' : 'Shot Quality',
          expectedMetricValue: isCricket ? 0.68 : isFootball ? 1.84 : 0.58,
          possessionHome: 62 + Math.round(Math.sin(frameCount * 0.05) * 8),
          pitchZone: isCricket ? 'Good Length Outside Off' : isFootball ? 'Final Third Left Half-Space' : 'Paint Isolation',
          defensiveLineHeightMeters: 46.2,
          aiNarrative: isCricket 
            ? 'Starc attempting yorker length to contain Kohli. High boundary probability detected.' 
            : isFootball 
            ? 'Man City overloading the right wing. Real Madrid defensive block shifted 4.2m deep.' 
            : 'Lakers running horns set for James drive to rim.'
        }
      };
      this.dispatch('TELEMETRY_UPDATE', telemetry);

      // 2. Crowd Decibels Fluctuation
      const crowd: CrowdDecibelSnapshot = {
        matchId: this.activeMatchId,
        currentDecibels: Math.round(92 + Math.sin(frameCount * 0.15) * 16 + Math.random() * 6),
        peakDecibels: 118.8,
        cheerCountTotal: 48250 + frameCount * 3,
        hypeLevel: (frameCount % 6 < 3) ? 'ROARING' : 'HYPED',
        vibeHapticThreshold: true
      };
      this.dispatch('CROWD_DECIBELS', crowd);

    }, 800);
  }

  private stopSimulation() {
    if (this.simulationTimer) {
      clearInterval(this.simulationTimer);
      this.simulationTimer = null;
    }
  }

  public getStatus(): boolean {
    return this.isConnected;
  }
}

export const wsClient = new WebSocketClient();
