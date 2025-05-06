This is a application created as a server to serve the platform where it helps in creating a marketers campaign brief by using previous data and leveraging Langchain and Langgraph.


## Folder Structure
This project follows a modular structure to organize the different components. The main source code resides within the src/ directory, while data, templates, logs, and output files are kept at the project root level.

Here's a breakdown of the key directories and files:
Server/
├── Data/                   # Input templates (Word .docx) and potentially other text data for RAG source
│   └── CampaignBriefCreationTemplate.docx  # Used as a template to create the campaign Brief
│   └── ... (other data files used for RAG indexing)
├── logos/                  # Image assets, specifically company logos
│   └── ... (logo files)
├── metadata/               # Metadata files (e.g., logo path mappings) used during vector store creation
│   └── ... (metadata files)
├── output/                 # **Final location for generated documents (.docx)**
│   └── (populated brief documents will be saved here)
├── src/                    # All Python source code for the application
│   ├── __init__.py         # Makes src a Python package
│   ├── app.py              # **Main Flask application script** - defines routes and invokes the workflow
│   ├── config.py           # Centralized configuration variables (paths, settings, etc.)
│   ├── llm.py              # Code to initialize the Azure OpenAI LLM and Embeddings instances
│   ├── rag.py              # Code to set up and initialize the Chroma vector store and Retriever
│   ├── tools/              # Langchain Tool definitions
│   │   ├── __init__.py     # Makes 'tools' a package; can be used to import all tools
│   │   ├── extract_placeholders.py  # Code for the 'extract_placeholders_from_template' tool
│   │   ├── populate_word.py     # Code for the 'populate_word_from_json' tool
│   │   ├── retrieve_data.py    # Code for the 'retrieve_relevant_campaign_data' tool
│   ├── agents/             # Langchain Agent definitions
│   │   ├── __init__.py     # Makes 'agents' a package; can be used to import all agents
│   │   ├── summarizer_agent.py  # Code for the Summarizer agent
│   │   ├── brief_generator_agent.py # Code for the Brief Generator agent
│   ├── workflows/          # Langgraph workflow definitions
│   │   ├── __init__.py     # Makes 'workflows' a package; can be used to import the compiled graph
│   │   ├── brief_generation_workflow.py # Defines the Langgraph supervisor workflow graph
│   └── utils/              # Custom helper functions or components not fitting other categories
│       ├── __init__.py     # Makes 'utils' a package
│       └── custom_supervisor.py # Example: Code for your custom create_supervisor function (if used)
├── .env                    # Environment variables file (for API keys, endpoints, etc.)
├── .gitignore              # Specifies intentionally untracked files that Git should ignore
├── build_vector_store.py   # Separate utility script to build/update the Chroma vector database
├── README.md               # Project documentation (this file)
└── requirements.txt        # List of Python dependencies for the project