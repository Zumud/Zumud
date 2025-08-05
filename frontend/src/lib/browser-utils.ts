export interface BrowserInfo {
  name: string
  settingsUrl: string | null
  instructions: string
  isBlocked?: boolean // Indicates if the browser blocks direct links to settings
}

// Browser detection for PDF viewer settings
export const getBrowserInfo = (): BrowserInfo => {
  if (typeof window === 'undefined') return { name: 'unknown', settingsUrl: null, instructions: 'Check your browser settings to enable PDF viewing' }
  
  const userAgent = window.navigator.userAgent.toLowerCase()
  
  if (userAgent.includes('chrome') && !userAgent.includes('edg') && !userAgent.includes('opr')) {
    return {
      name: 'Chrome',
      settingsUrl: 'chrome://settings/content/pdfDocuments',
      instructions: 'Go to Chrome Settings > Privacy and security > Site Settings > PDF documents > Disable "Download PDF files instead of automatically opening them in Chrome"',
      isBlocked: true
    }
  } else if (userAgent.includes('firefox')) {
    return {
      name: 'Firefox',
      settingsUrl: 'about:preferences#pdfjs',
      instructions: 'Go to Firefox Settings > General > Applications > Find "Portable Document Format (PDF)" and set to "Preview in Firefox"',
      isBlocked: false // Firefox about: URLs usually work
    }
  } else if (userAgent.includes('safari') && !userAgent.includes('chrome')) {
    return {
      name: 'Safari',
      settingsUrl: null,
      instructions: 'Safari > Preferences > Websites > PDF - Set to "View in browser"',
      isBlocked: false
    }
  } else if (userAgent.includes('edg')) {
    return {
      name: 'Edge',
      settingsUrl: 'edge://settings/content/pdfDocuments',
      instructions: 'Go to Edge Settings > Cookies and site permissions > PDF documents > Disable "Always open PDF files externally"',
      isBlocked: true
    }
  } else if (userAgent.includes('opr')) {
    return {
      name: 'Opera',
      settingsUrl: 'opera://settings/content/pdfDocuments',
      instructions: 'Go to Opera Settings > Advanced > Privacy and security > Site Settings > PDF documents',
      isBlocked: true
    }
  }
  
  return {
    name: 'your browser',
    settingsUrl: null,
    instructions: 'Check your browser settings to enable PDF viewing'
  }
}