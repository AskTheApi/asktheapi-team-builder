# AutoGen Team Builder

[![PyPI version](https://badge.fury.io/py/autogen-team-builder.svg)](https://badge.fury.io/py/autogen-team-builder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/autogen-team-builder.svg)](https://pypi.org/project/autogen-team-builder/)

A high-level Python library for easily building and managing teams of AutoGen agents. This package provides a clean, type-safe interface for creating, configuring, and running teams of agents that can work together to solve complex tasks.

## Features

- 🚀 Easy creation of individual agents with custom tools and capabilities
- 🤝 Team building with automatic coordination through a planning agent
- 📡 Support for streaming agent interactions
- 🔧 Built-in HTTP client for tool implementation
- ✨ Pydantic models for type safety and validation
- 🎯 Clean, intuitive API design

## Installation

```bash
pip install autogen-team-builder
```

## Quick Start

Here's a simple example of how to use the package:

```python
from autogen_team_builder import TeamBuilder, Agent, Tool, Message

# Define your agents
calculator = Agent(
    name="Calculator",
    description="A math expert that can perform calculations",
    system_prompt="You are a math expert. Help solve mathematical problems.",
    tools=[
        Tool(
            name="calculate",
            description="Perform a calculation",
            method="POST",
            path="/calculate",
            jsonschema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                }
            }
        )
    ]
)

researcher = Agent(
    name="Researcher",
    description="An agent that can search and summarize information",
    system_prompt="You are a research expert. Find and summarize information.",
    tools=[
        Tool(
            name="search",
            description="Search for information",
            method="GET",
            path="/search",
            jsonschema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        )
    ]
)

# Create a team builder
team_builder = TeamBuilder(model="gpt-4")

# Build the team
team = await team_builder.build_team([calculator, researcher])

# Run the team with a task
messages = [
    Message(
        role="user",
        content="Calculate the square root of 16 and then find some interesting facts about the number 4."
    )
]

result = await team_builder.run_team(team, messages)
```

## Advanced Usage

### Custom Tool Implementation

You can create agents with custom tools that interact with your APIs:

```python
agent = Agent(
    name="WeatherAgent",
    description="Provides weather information",
    system_prompt="You are a weather expert.",
    base_url="https://api.weather.com",
    tools=[
        Tool(
            name="get_weather",
            description="Get weather for a location",
            method="GET",
            path="/weather",
            jsonschema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "units": {"type": "string", "enum": ["metric", "imperial"]}
                },
                "required": ["location"]
            }
        )
    ]
)
```

### Streaming Support

You can stream the agent interactions:

```python
async for event in team_builder.run_team(team, messages, stream=True):
    if isinstance(event, ChatMessage):
        print(f"{event.source}: {event.content}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/alexalbala/autogen-team-builder.git
cd autogen-team-builder

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [Microsoft's AutoGen](https://github.com/microsoft/autogen)
- Inspired by the need for a higher-level interface for agent team management 