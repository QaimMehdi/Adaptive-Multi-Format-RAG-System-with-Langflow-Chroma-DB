import os
import argparse
import sys

# Load environment variables from .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def run_rag_flow(query: str, flow_path: str = "flow.json"):
    # Ensure flow.json exists in workspace
    if not os.path.exists(flow_path):
        print(f"Error: {flow_path} not found in this directory.", file=sys.stderr)
        print("Please export your flow as JSON from Langflow and save it as flow.json.", file=sys.stderr)
        sys.exit(1)
        
    # Warn if API keys are missing in the local environment
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("Warning: Neither GEMINI_API_KEY nor OPENAI_API_KEY was found in your environment variables.", file=sys.stderr)
        print("Please check your .env file or export the keys before running.", file=sys.stderr)

    try:
        from langflow.load import run_flow_from_json
    except ImportError:
        print("Error: 'langflow' package is not installed in your current Python environment.", file=sys.stderr)
        print("Please install it using: pip install langflow python-dotenv", file=sys.stderr)
        sys.exit(1)

    print(f"Sending query to Langflow RAG pipeline: '{query}'...")
    try:
        # Run the flow using the sanitized flow.json, allowing it to fall back to environment variables
        results = run_flow_from_json(
            flow=flow_path,
            input_value=query,
            fallback_to_env_vars=True  # Resolves placeholders like ${GEMINI_API_KEY} from environment
        )
        
        # Display flow output
        if results:
            print("\n" + "=" * 50)
            print("                     RAG RESPONSE")
            print("=" * 50)
            try:
                # Attempt to extract text from the standard Langflow output wrapper
                outputs = results[0].outputs[0]
                message = outputs.messages[0]
                print(message.text)
            except Exception:
                # Fallback to printing raw output if the schema differs
                print(results)
            print("=" * 50 + "\n")
        else:
            print("No output received from the flow.")
            
    except Exception as e:
        print(f"An error occurred while executing the flow: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Langflow Multi-Format RAG pipeline programmatically.")
    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        help="The query/question to ask the RAG pipeline."
    )
    parser.add_argument(
        "--flow",
        type=str,
        default="flow.json",
        help="Path to the Langflow JSON file (default: flow.json)."
    )
    
    args = parser.parse_args()
    
    if args.query:
        run_rag_flow(args.query, args.flow)
    else:
        # Fallback to an interactive command-line interface
        print("=" * 60)
        print("    Langflow Multi-Format RAG - Interactive CLI Terminal")
        print("=" * 60)
        print("Type 'exit' or 'quit' to terminate the session.\n")
        while True:
            try:
                user_input = input("Question: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting RAG CLI terminal. Goodbye!")
                    break
                run_rag_flow(user_input, args.flow)
            except KeyboardInterrupt:
                print("\nSession interrupted. Goodbye!")
                break
