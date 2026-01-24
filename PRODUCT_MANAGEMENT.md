# Product Management Overview – AI Project Risk Predictor

## Product Overview
The AI Project Risk Predictor was built to support better project decision-making using data rather than intuition alone.  
In many teams, project health is assessed through manual updates, meetings, or subjective judgments. This product introduces a simple, structured way to identify risk early and guide next steps.

The goal is not to replace project managers, but to **support them with clearer signals and faster insights**.

---

## Problem Statement
Project risks are often identified late, when delays or failures have already occurred. Information is usually scattered across spreadsheets, tools, and status meetings, making it hard to see early warning signs.

Some common issues observed:
- Project risks are flagged too late
- Risk assessment varies from person to person
- Managers spend significant time preparing reports
- Decisions are made without consistent data support

This product addresses these problems by converting project data into a risk score and a clear recommended action.

---

## Target Users
This product is designed for:
- Project Managers
- Team Leads
- Engineering Managers
- Business Stakeholders who review project status

These users typically need **quick, understandable answers**, not technical details.

---

## Key Features Delivered
- Upload project data and generate predictions
- Identify whether a project is on track, delayed, or critical
- Assign a numerical risk score to support comparison
- Convert predictions into clear actions (GO, HOLD, ESCALATE)
- Provide a short explanation for each recommendation
- Visualize results using Power BI dashboards
- Track work and risks using a Jira-based workflow

Each feature was designed to reduce manual effort and improve visibility.

---

## Decision Workflow (End-to-End)
The system follows a simple and transparent workflow:

1. Project data is provided as a CSV file
2. A machine learning model predicts project outcome and risk score
3. A Java-based rule layer converts predictions into actions
4. Results are exported in a clean format
5. Power BI dashboards present insights to stakeholders

This separation allows each part of the system to be updated independently.

---

## Metrics and Success Indicators
If this product were used in a real organization, success would be measured using:

- Number of high-risk projects identified early
- Reduction in delayed or failed projects
- Time saved in weekly reporting
- Usage of the dashboard by managers
- Consistency in decision-making across teams

These metrics focus on **practical impact**, not just model performance.

---

## Assumptions and Constraints
To keep the product lightweight and easy to deploy, the following assumptions were made:

- Project data is provided in CSV format
- The system is designed for small to medium datasets
- Authentication and access control are not included in this version
- Predictions are based on historical project patterns

These choices were intentional to keep the scope realistic.

---

## Future Roadmap
Planned improvements for future versions include:
- Pulling live project data directly from Jira using APIs
- Storing historical results in a database for trend analysis
- Tracking risk changes over time
- Adding basic authentication and role-based access
- Supporting multiple teams and projects in one dashboard

These enhancements would make the product suitable for larger organizations.

---

## Product Management Approach
This project was developed with a product mindset rather than a purely technical one.

Key principles followed:
- Focus on clarity over complexity
- Translate analytics into actionable decisions
- Design for non-technical users
- Keep the system modular and maintainable
- Balance accuracy with usability and speed

The result is a practical tool that connects data, decisions, and project outcomes in a meaningful way.

