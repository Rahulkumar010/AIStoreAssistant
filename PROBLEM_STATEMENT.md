# Agentic AI Hackathon 2025: AI Store Assistant

# Situation

In today's competitive retail environment, multi-location store chains face increasing
pressure to deliver consistent performance, superior customer experiences, and
operational efficiency, all while managing rising costs and shifting consumer
expectations.

Sainbury's, a chain of retail stores in the UK, collects data from numerous sources such
as sales systems, customer feedback platforms, surveillance footage, inventory tools,
and staffing systems. However, this data often remains fragmented, analyzed in
isolation, and rarely provides a unified picture & insights on store performance and
areas for improvement.


# Objective

Develop a Gen Al-powered Store Assistant that unifies structured data (such as sales
orders, staffing, inventory, etc.) with unstructured data (customer reviews, videos, and
images, etc.) to deliver comprehensive insights into store performance. The assistant
should analyze key metrics such as, but not limited to, layout, queue wait times, staff
interactions, shelf stocking, etc., to support informed, data-driven decisions. It should
also monitor visual inputs to trigger alerts for issues like long queues, low staffing,
empty shelves, etc., and provide actionable recommendations through an interactive
conversational interface, enabling users to query performance metrics and receive
intelligent insights that enhance operational efficiency and customer experience.
Teams are expected to leverage OpenAl models to build the assistant, utilizing Agentic
Al Workflows for effective data retrieval, reasoning, and decision making for Insights. A
Streamlit-based user interface will provide a seamless, user-friendly experience,
allowing for dynamic interactions and customized recommendations.

# Functionalities

An ideal Store Assistant should empower the
Store Manager by providing actionable insights
into key performance metrics, enabling data-
driven decisions that enhance operational
efficiency and elevate the customer experience
through proactive analysis, alerts, and intelligent
recommendations

Considerations for store performance may
include, but are not limited to:
· Sales performance
. Waiting timings at billing counter
. Cleanliness of the store
· Utilization of staff
. Empty shelves on the aisle
. Interaction of staff
.... etc.


# Analyze web-based customer reviews and identify sentiment

· Analyze online reviews and determine sentiment across different themes such as waiting
time, staff behavior, cleanliness, ease of locating items, etc., for each store. Assign
appropriate weightages for each metric and generate a sentiment scorecard for each store
across different themes

# Video & Image Analysis for Insights

· Create a scorecard to evaluate the store based on video & images for each store. Set up an
Agentic Al pipeline to extract the information and leverage these metrics to develop a
scorecard (e.g., store cleanliness, empty shelves, long queues). Provide flexibility for the
end user to modify the weightages through UI and regenerate the scorecard.

# Data Analyzer and Reporting

. Develop an Agentic workflow to seamlessly interact with the scorecards and the structured
data. Implement an agent capable of interpreting natural language queries and generating
insights/responses from transactional & related datasets.
· Generate a one-pager integrated report for executive stakeholders summarizing key
highlights, indicating store performance such as sales, avg. order value, integrated
scorecard, etc., extracted from structured / unstructured data and insights for the store.
. Additionally, provide flexibility through UI for the user to query on the data (e.g., Why is one
store performing better than another, how do operational factors affect sales, what are
early warning signals for declining performance, etc.)

# Store Monitoring

. Build workflows to trigger alerts to the Store manager based on the activities in the
video/images, which should help the Store manager take necessary actions to improve the
overall customer experience and score of the store. Examples of alerts would be 'empty
shelves', 'spilled aisles', 'long queue on billing counters' etc.

# Interactive UI With Feedback Loop

. Design an intuitive interface leveraging Streamlit that allows store managers to view and
interact with insights & recommendations. The interface should provide flexibility for
querying on data for additional insights, flexibility to modify weightages for the scorecard,
etc.


# Data

# Inputs

. Input to the tool would be images and videos of the store.

. Additionally end users should have the flexibility to ask queries and
regenerate recommendations

# Store data

· Store data has information about the sales, staff, and location data.


# Hackathon Deliverables

# Codebase

. All the python files must be submitted in a zip
folder with all the requirements.
. Vector store index & supporting artifacts (if
leveraged)
. Add documentation describing the steps to
run the code base

# Video & Presentation

· Create a walkthrough video (5 min max)
explaining the approach and codebase
. A PowerPoint deck (not more than 5 slides)
covering the following
o Methodology and decision-making
strategy incorporated
o Process flow diagram outlining the steps
and tools involved in the solution
o Ul snapshots illustrating the
functionalities and Q&A Capabilities

# Generated Outputs

. Store scorecards table

. Alert system for the Store

In live demo, the tool is expected to provide
insights & alerts for the provided test cases