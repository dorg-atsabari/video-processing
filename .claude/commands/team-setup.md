# Team Setup Command

You are setting up a customizable team of agents. Follow these steps exactly:

## Step 1: Gather Team Configuration

Use the `AskUserQuestion` tool to ask the user the following questions in a single prompt:

1. **How many teammates?** — Offer options: 2, 3, 4 (let them pick or type a custom number)
2. **What is the team name?** — Offer a few suggestions like "project-team", "feature-team", "dev-team", or let them type a custom name

Wait for the user's answers before proceeding.

## Step 2: Gather Roles

Based on the number of teammates chosen, use `AskUserQuestion` to ask for the **role of each teammate**, one question per teammate. For each teammate, offer these specialized role presets:

- **Python Engineer** — Expert in Python, PyAV, OpenCV, and video processing pipelines. Designs and implements frame-level processing logic, face-tracking algorithms (exponential smoothing, dead zones, snap thresholds), video muxing with PyAV, and audio/video stream handling. Writes production-grade Python with proper error handling, type hints, and logging. (subagent_type: `senior-backend-engineer` — custom agent defined in `.claude/agents/senior-backend-engineer.md`)
- **ML/CV Engineer** — Expert in computer vision and machine learning model integration. Specializes in OpenCV face detection backends (Haar cascades, YuNet ONNX via `cv2.FaceDetectorYN`), ONNX model lifecycle management, detection tuning (min_size, confidence thresholds), and integrating new CV backends into the pluggable `face_detector/` package. (subagent_type: general-purpose)
- **Architect** — Expert in system design for Python toolkits: pipeline architecture, pluggable backend patterns (factory/strategy), package structure, performance trade-offs (multiprocessing vs threading for CPU-bound frame processing), testability, and API surface design. Produces architectural decision records and implementation plans. (subagent_type: `senior-software-architect` — custom agent defined in `.claude/agents/senior-software-architect.md`)
- **QA Engineer** — Expert in quality assurance for Python projects: pytest test strategy, unit and integration testing, mocking PyAV and OpenCV objects, edge case analysis (missing frames, no face detected, codec errors), code coverage, and regression testing. Writes thorough test suites and validates pipeline correctness. (subagent_type: `senior-qa-engineer` — custom agent defined in `.claude/agents/senior-qa-engineer.md`)
- **DevOps/Tooling Engineer** — Expert in Python project tooling and infrastructure: packaging (`pyproject.toml`, `pip install -e`), CI/CD pipelines (GitHub Actions), dependency management, model file distribution (ONNX assets), environment reproducibility, and build automation. (subagent_type: general-purpose)
- **Security Engineer** — Expert in application security: secure handling of external URLs and user-supplied file paths, dependency auditing, secrets management, input validation, and secure coding practices for a Python video processing toolkit. (subagent_type: general-purpose)

The user can also type a custom role. Ask all teammate roles in a single AskUserQuestion call (up to 4 questions).

**Important:** When spawning a teammate, include their full expertise description in the agent prompt so they adopt that professional persona throughout their work.

## Step 3: Gather the Work

Use `AskUserQuestion` to ask: **"What work should this team accomplish?"** — This is a free-text field, so offer a couple of example options but let them type their own detailed description.

## Step 4: Create the Team

1. Use `TeamCreate` to create the team with the chosen name
2. Use `TaskCreate` to break down the user's work description into individual tasks appropriate for the roles chosen
3. Spawn each teammate using the `Task` tool with:
   - `team_name` set to the team name
   - `name` set to a short identifier based on their role (e.g., "python-engineer", "cv-engineer", "architect", "tester")
   - `subagent_type` mapped from their role:
     - Python Engineer → `senior-backend-engineer` (custom agent from `.claude/agents/senior-backend-engineer.md`)
     - QA Engineer → `senior-qa-engineer` (custom agent from `.claude/agents/senior-qa-engineer.md`)
     - Architect → `senior-software-architect` (custom agent from `.claude/agents/senior-software-architect.md`)
     - ML/CV Engineer, DevOps/Tooling Engineer, Security Engineer → `general-purpose` (until their custom agent files are created)
   - `mode` set to `bypassPermissions` for roles that write code/files (Python Engineer, ML/CV Engineer, QA Engineer, DevOps/Tooling Engineer), `default` for advisory roles (Architect, Security Engineer)
   - A detailed `prompt` that includes:
     - Their full professional expertise description from Step 2
     - The team context and project background: this is a **Python video processing toolkit** that trims, crops, and face-tracks video files using PyAV and OpenCV, with a pluggable `face_detector/` package supporting yunet (ONNX) and haar backends
     - Instructions to check TaskList for available work
     - A directive to approach all tasks through the lens of their specialization
4. Use `TaskUpdate` to assign tasks to the appropriate teammates based on their roles

## Step 5: Report

Summarize the team setup to the user:
- Team name
- Number of teammates and their roles
- Tasks created and assignments
- How to interact with the team (they can talk to you and you'll coordinate)

$ARGUMENTS
