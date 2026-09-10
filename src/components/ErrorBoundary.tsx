import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error('React error boundary caught an error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-screen flex items-center justify-center bg-slate-900 text-slate-100 p-8">
          <div className="max-w-2xl w-full bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
            <h1 className="text-xl font-semibold text-red-400 mb-4">应用启动失败</h1>
            <p className="text-sm text-slate-300 mb-4">
              请把下面的错误信息复制给开发者，或尝试重新运行 <code>npm run build</code> 后重试。
            </p>
            <pre className="bg-slate-950 text-red-300 p-4 rounded-lg text-xs overflow-auto max-h-96">
              {this.state.error?.toString()}
            </pre>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
