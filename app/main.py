import logging
from typing import Dict
import ollama
from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """

    # Retrieve input
    request: InputClass = model.request

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"{configurations}")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else []
    stub = Stub(app_ids)

    # ------------------------------
    # TODO : add your magic here
    # ------------------------------
    # Call the Text to Image app
    # object = stub.call('c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network', {'prompt': 'Make me a glowing dragon standing on a cliff at sunset.'}, 'super-user')
    
    logging.info(f"User prompt: {request.prompt}")
    try:
        #Step 1: Local DeepSeek prompt enhancement via Ollama
        
        response = ollama.chat(
            model='deepseek-coder',  
            messages=[{
                'role': 'user',
                'content': f"Expand this visual idea for art generation with detailed style, emotion, and environment: \"{request.prompt}\""
            }]
        )
        expanded_prompt = response['message']['content'].strip()
        logging.info(f"Expanded prompt from DeepSeek: {expanded_prompt}")
    
    except Exception as e:
        logging.error(f"Error calling DeepSeek via Ollama: {e}")
        expanded_prompt = request.prompt

    #Response back
    response: OutputClass = model.response
    response.message = (
        f"Original Prompt: {request.prompt}\n"
        f"Expanded Prompt: {expanded_prompt}"
    )
        
    #Step 2: Call the Text to Image app
    logging.info(f"Expanded prompt from DeepSeek: {expanded_prompt}")

    image_response = stub.call(
        'f0997a01-d6d3-a5fe-53d8-561300318557.node3.openfabric.network',
        {'prompt': expanded_prompt},
        'super-user'
        )

    image = image_response.get('result')

    # Save to file
    with open('output.png', 'wb') as f:
        f.write(image)

    logging.info("Image saved as output.png")
    
    #Step 3: Image to 3D Model
    
    logging.info(f"Expanded prompt from DeepSeek: {image}")

    try:
        with open('output.png', 'rb') as f:
            image_bytes = f.read()

        model_response = stub.call(
            '69543f29-4d41-4afc-7f29-3d51591f11eb.node3.openfabric.network',  # Image-to-3D app Id
            {'image': image_bytes},
            'super-user'
        )

        model_data = model_response.get('result')

        with open('output.glb', 'wb') as f:
            f.write(model_data)

        logging.info("3D model saved as output.glb")

    except Exception as e:
        logging.error(f"Failed to generate 3D model: {e}")
        