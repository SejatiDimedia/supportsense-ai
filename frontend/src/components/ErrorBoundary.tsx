import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('SupportSense UI Error Boundary caught an unhandled exception:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen w-screen items-center justify-center bg-[#070A0F] p-6 text-white font-sans">
          <div className="max-w-md w-full rounded-2xl border border-red-500/20 bg-[#0E1116] p-8 shadow-2xl space-y-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/10 text-red-400">
              <AlertTriangle className="h-6 w-6" />
            </div>

            <div className="space-y-1">
              <h2 className="text-base font-semibold text-white">
                Application Runtime Exception
              </h2>
              <p className="text-xs text-slate-400">
                SupportSense AI console encountered an unexpected interface error.
              </p>
            </div>

            {this.state.error && (
              <div className="rounded-xl border border-white/[0.08] bg-black/40 p-3 font-mono text-[11px] text-red-300 break-words">
                {this.state.error.message || 'Unknown runtime error'}
              </div>
            )}

            <button
              onClick={this.handleReload}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-lime-400 px-4 py-2.5 text-xs font-semibold text-black transition-all hover:bg-lime-300"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Reload Console</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
