import { useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function SubmitButton() {
  return (
    <button type="submit">Submit</button>
  )
}

function SolutionFileInput({ onChange }) {
  return (
    <input
      id="solution"
      name="solution"
      type="file"
      accept=".cc,.cpp,.cxx,.c,.h,.hpp"
      required
      onChange={onChange}
    />
  )
}

function App() {
  const [message, setMessage] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    const file = event.currentTarget.elements.solution.files[0]

    if (file) {
      setMessage(`Demo submission: ${file.name}`)
    }
  }

  return (
    <main>
      <h1>IPL</h1>

      <h2>Problem</h2>
      <p>Problem description goes here.</p>

      <h3>Hi</h3>
      <pre>input here</pre>

      <h3>Hi</h3>
      <pre>output here</pre>

      <h2>Submit a solution</h2>
      <form onSubmit={handleSubmit}>
      <label htmlFor="solution">C++ source file </label>
      <SolutionFileInput onChange={() => setMessage('')} />
      <SubmitButton />
      </form>

      <p role="status">{message}</p>
    </main>
  )
}
export default App
