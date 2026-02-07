function Nav() {
  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-black px-6">
      <div className="mx-auto flex h-14 items-center justify-between px-4">
        <a href="/" className="flex items-center gap-2 font-semibold tracking-tight text-white no-underline">
          <span className="text-2xl font-medium">ClinSearch</span>
        </a>
      </div>
    </nav>
  )
}

export default Nav
