// Runs before paint to set the initial theme from localStorage (falling back to
// the OS preference). Prevents a flash of the wrong theme (FOUC) and keeps the
// <html> class in sync with what ThemeToggle reads/writes.
export function ThemeScript() {
  const code = `(function(){try{var t=localStorage.getItem('theme');var m=window.matchMedia('(prefers-color-scheme: dark)').matches;var dark=t==='dark'||(!t&&m);document.documentElement.classList.toggle('dark',dark);document.documentElement.style.colorScheme=dark?'dark':'light';}catch(e){}})();`;
  return <script dangerouslySetInnerHTML={{ __html: code }} />;
}
