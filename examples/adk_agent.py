"""
Example of integrating Google Maps MCP Server with Google ADK.

This example shows how to create an intelligent location agent using ADK
that can answer complex queries combining multiple Google Maps tools.
"""

import asyncio
import os
from typing import Any

from dotenv import find_dotenv, load_dotenv

# Note: This example requires Google ADK to be installed
# pip install google-adk

try:
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("Warning: Google ADK not installed. Install with: pip install google-adk")


async def create_location_agent() -> Agent | None:
    """Create an ADK agent with Google Maps MCP tools."""

    if not ADK_AVAILABLE:
        print("Cannot create agent: Google ADK not installed")
        return None

    # Get API key from environment
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY not set")
        return None

    # Get Gemini API key from environment (required for the agent model)
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        print("Error: GOOGLE_API_KEY or GEMINI_API_KEY not set")
        print("This is required for the agent model")
        print("Please set it in your .env file or environment variables")
        return None

    # Get model name from environment (default to gemini-2.0-flash)
    model_name = os.getenv("AGENT_MODEL", "gemini-2.0-flash")
    print(f"Using model: {model_name}")

    # Create Google Maps MCP toolset
    print("Creating Google Maps MCP toolset...")
    maps_tools = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="google-maps-mcp-server", env={"GOOGLE_MAPS_API_KEY": api_key}
            )
        )
    )

    # Create ADK agent with Maps tools
    agent = Agent(
        name="location_intelligence_agent",
        model=model_name,
        instruction="""You are a helpful location intelligence assistant with access to
        real-time Google Maps data. You can:

        - Find places and points of interest
        - Get directions and route planning with traffic
        - Geocode addresses and reverse geocode coordinates
        - Calculate distances and travel times
        - Analyze GPS traces and road networks
        - Provide speed limit information for safety

        When answering queries:
        1. Use the appropriate tools to gather accurate, real-time data
        2. Provide specific, actionable information
        3. Include relevant details like distances, times, ratings, and addresses
        4. Suggest alternatives when appropriate
        5. Be concise but thorough

        Always prioritize user safety and provide current traffic information when relevant.
        """,
        tools=[maps_tools],
    )

    return agent


async def run_example_queries(runner: Any) -> None:
    """Run example queries through the agent."""

    queries: list[dict[str, str]] = [
        # Query 1: Restaurant recommendation
        {
            "query": "I'm at Times Square in New York. Find me the top 3 rated Italian restaurants within walking distance (500m).",
            "description": "Restaurant search with filters",
        },
        # Query 2: Route planning with traffic
        {
            "query": "What's the fastest route from San Francisco to Los Angeles right now? How long will it take with current traffic?",
            "description": "Route planning with real-time traffic",
        },
        # Query 3: Address lookup
        {
            "query": "What are the coordinates for the Eiffel Tower in Paris? And what's the full address?",
            "description": "Geocoding landmark",
        },
        # Query 4: Reverse geocoding
        {
            "query": "What's located at coordinates 51.5074, -0.1278?",
            "description": "Reverse geocoding coordinates",
        },
        # Query 5: Fleet optimization question
        {
            "query": "I need to visit these three locations starting from Central Park: MoMA, Brooklyn Museum, and the Guggenheim. What's the most efficient route and total travel time?",
            "description": "Multi-stop route optimization",
        },
    ]

    print("=" * 80)
    print("RUNNING EXAMPLE QUERIES")
    print("=" * 80)
    print()

    for i, example in enumerate(queries, 1):
        print(f"Query {i}: {example['description']}")
        print(f"User: {example['query']}")
        print("-" * 80)

        # Run query through agent
        events = await runner.run_debug(
            example["query"], quiet=True, session_id=f"example_query_{i}"
        )

        # Print response
        print("Agent: ", end="", flush=True)
        for event in events:
            if event.author == "location_intelligence_agent" and event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="")
        print()
        print()
        print("=" * 80)
        print()


async def interactive_mode(runner: Any) -> None:
    """Run agent in interactive mode."""

    print("=" * 80)
    print("INTERACTIVE MODE")
    print("=" * 80)
    print()
    print("Ask me anything about locations, directions, or places!")
    print("Type 'exit' or 'quit' to end the session.")
    print()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            # Get agent response
            print()
            print("Agent: ", end="", flush=True)
            events = await runner.run_debug(
                user_input, quiet=True, session_id="interactive_session"
            )
            for event in events:
                if event.author == "location_intelligence_agent" and event.is_final_response():
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                print(part.text, end="")
            print()
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()


async def main() -> None:
    """Main function."""
    load_dotenv(find_dotenv())

    # Create agent
    agent = await create_location_agent()

    if not agent:
        return

    # Create runner
    runner = InMemoryRunner(agent=agent)

    print("Agent created successfully!")
    print()

    # Run example queries
    print("Running example queries...")
    print()
    await run_example_queries(runner)

    # Start interactive mode
    print("Starting interactive mode...")
    print()
    await interactive_mode(runner)


if __name__ == "__main__":
    if not ADK_AVAILABLE:
        print("This example requires Google ADK to be installed.")
        print("Install it with: pip install google-adk")
    else:
        asyncio.run(main())
