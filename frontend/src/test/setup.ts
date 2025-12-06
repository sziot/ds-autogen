import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// 自动清理
afterEach(() => {
  cleanup();
});

// Mock WebSocket
global.WebSocket = class WebSocket {
  url: string;
  readyState: number;
  onopen: ((this: WebSocket, ev: Event) => any) | null;
  onmessage: ((this: WebSocket, ev: MessageEvent) => any) | null;
  onerror: ((this: WebSocket, ev: Event) => any) | null;
  onclose: ((this: WebSocket, ev: CloseEvent) => any) | null;

  constructor(url: string) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.onclose = null;
  }

  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  send() {}
  close() {}
} as any;

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: () => <div data-testid="mock-monaco-editor" />,
}));

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});