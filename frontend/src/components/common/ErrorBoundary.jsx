import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can log error info here if needed
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ color: 'red', background: '#fff3f3', padding: 16, borderRadius: 8, margin: 16 }}>
          <h2>Something went wrong while rendering the results.</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 14 }}>{String(this.state.error)}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;