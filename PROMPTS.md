# PROMPTS.md

hi we havelook git repo is set backend frontend folder is dne here is setup ss attached now lets start with code so dont this in one time we sholud itrate the whole thing that will good so before genrateeing code make sure the context file sholud be genarte if tokens ends we will try another thing tech stack i  prefer is react and fastapi for llm groq api and the mention all features of ai i love to integrate so concept is there will three persona super admin manager and employee lets crack it lets start with backend api and db setup and we will test api n postman then we will move to frontend t ghe end an assignmment first understand it and discuss with me deadline is 2hrs only there is mentioned 3 but in real 2hrs

Q: Which AI features do you want to integrate? (pick all you want) (Select all that apply)
A: Natural language leave apply (chat → auto-fill form), Smart approval insights for managers, Pattern detection (flags suspicious leave trends), Conversational leave assistant (full chat interface)

Q: What database are you going with?
A: SQLite (fastest to set up, no install)

Q: For auth — how simple do you want it?
A: Simple JWT (email+password, no OAuth)

right this my directory now give me cmd commands to create this backend files in backend folder then i will paste the code

start the react part keep it simple so debugging will not be the issue no complex ui libaries and but it looks like a good dashboard try to do on baic inaries but good looking ui

hi i am wroking on a assingment and actually got out of tokens now the frontendd part is remaining here is context md and the forntend tech stack details give the frontedn minimal but good looking and desktop and mobile freindly most needed  and no bugs plese the dealine is hitting here is the fontedn stack and setup ss

Here’s a clear, quick overview of your frontend stack based on your project:

🧱 Core Stack (what you’re using)

1. ⚛️ React

* UI library for building components
* Everything is component-based (App.jsx, pages, UI blocks)

Example:
function App() {
return <h1>Hello</h1>
}

2. ⚡ Vite

* Build tool + dev server
* Replaces older tools like Webpack
* Gives fast startup + hot reload

What it does:

* Runs your app locally (npm run dev)
* Bundles code for production

3. 🟨 JavaScript (JSX)

* You’re writing React using JSX (HTML inside JS)

4. 🎨 CSS

* Styling via:

  * index.css
  * component styles

5. 📦 Node.js + npm

* Used to:

  * install packages
  * run scripts
  * manage dependencies

🔌 Plugins
@vitejs/plugin-react

* Connects React with Vite
* Enables:

  * JSX support
  * Fast refresh

📁 Project Structure (your setup)

frontend/
├── src/
│   ├── assets/       → images (hero.png etc.)
│   ├── App.jsx       → main component
│   ├── main.jsx      → entry point
│   └── index.css     → styles
├── index.html        → root HTML
├── vite.config.js    → config
└── package.json      → dependencies

🔁 How everything works together

1. main.jsx → loads React app into index.html
2. App.jsx → main UI
3. Vite → runs server + reloads on change
4. Browser → shows UI

🎯 In one line
You’re using React (UI) + Vite (build/dev server) + Node/npm (tooling)

💡 What you are NOT using (important)

* No Next.js (no backend rendering)
* No Redux (state management yet)
* No TypeScript (pure JS)

If interviewer asks:
“I built the frontend using React with Vite for fast development and hot reloading. The app is component-based, styled with CSS, and managed using npm.”

backend error for groq ai chat

def get_groq_client() -> Groq:
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
return Groq(api_key=api_key)

MODEL = "llama-3.3-70b-versatile"

bug for select leave so fisrt instead of solving this go through whole frontend nd find all bugs and change them
