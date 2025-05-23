import argparse
import yaml
from vllm import LLM, SamplingParams

def extract_questions(yaml_file):
    """
    Extracts all questions from the 'questions_and_answers' sections of the YAML file.

    Args:
        yaml_file (str): Path to the qna.yaml file.

    Returns:
        list: A list of questions extracted from the YAML file.
    """
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    questions = []
    # Navigate through the YAML structure to find all questions
    seed_examples = data.get('seed_examples', [])
    for example in seed_examples:
        qna_list = example.get('questions_and_answers', [])
        for qna in qna_list:
            question = qna.get('question')
            if question:
                # Clean up the question if it starts with 'Q: ' or similar prefixes
                if question.lower().startswith('q:'):
                    question = question[2:].strip()
                questions.append(question)
    return questions

def query_model(llm, system_prompt, question):
    """
    Constructs the prompt and queries the model to get the answer.

    Args:
        llm (LLM): The language model instance.
        system_prompt (str): The system prompt to set the model's context.
        question (str): The question to query.

    Returns:
        str: The answer generated by the model.
    """
    prompt = f"<|system|>{system_prompt}<|user|>{question}<|assistant|>"

    sampling_params = SamplingParams(
        max_tokens=200,
        temperature=0,
    )

    response_generator = llm.generate(prompt, sampling_params)
    answer = ""

    for response in response_generator:
        # Debugging: Print the entire response object
        #print("\n--- Debugging Response ---")
        #print(response)
        #print("--- End of Response ---\n")

        # Check if 'outputs' exist and have at least one CompletionOutput
        if hasattr(response, 'outputs') and len(response.outputs) > 0:
            completion = response.outputs[0]
            if hasattr(completion, 'text'):
                answer += completion.text.strip()
            else:
                print("Debug: 'text' attribute not found in CompletionOutput.")
        else:
            print("Debug: 'outputs' not found or empty in the response.")

    return answer

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Query model with questions from a YAML file.')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the language model.')
    parser.add_argument('--yaml_file', type=str, required=True, help='Path to the qna.yaml file.')
    args = parser.parse_args()

    # Extract questions from the YAML file
    questions = extract_questions(args.yaml_file)

    # Initialize the language model
    llm = LLM(
        model=args.model_path,
        # dtype="bfloat16",  # Adjust dtype as needed
    )

    # Define the system prompt
    system_prompt = (
        "I am a Red Hat® Instruct Model, an AI language model developed by Red Hat and IBM Research "
        "based on the granite-3.0-8b-base model. My primary role is to serve as a chat assistant."
    )

    # Iterate over each question, query the model, and print the Q&A
    for idx, question in enumerate(questions, 1):
        answer = query_model(llm, system_prompt, question)
        print(f"Q{idx}: {question}")
        print(f"A{idx}: {answer}\n")

if __name__ == '__main__':
    main()
