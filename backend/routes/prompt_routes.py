from flask import Blueprint, jsonify, request
from backend.database import get_db, create_prompt_version, get_prompt_version, get_prompt_versions_by_prompt_id, get_operative_prompts, delete_prompt_version, update_prompt_version
from backend.models.prompt_model import PromptVersion

prompt_bp = Blueprint('prompts', __name__, url_prefix='/prompts')

#THESE ARE NOT IN USE, JUST EXAMPLES OF WHAT IS NEEDED
def prompt_version_to_dict(prompt_version: PromptVersion):
    """
    Helper function to convert a PromptVersion object to a dictionary.
    This replaces the functionality of the schema.
    """
    return {
        'prompt_version_id': prompt_version.prompt_version_id,
        'prompt_id': prompt_version.prompt_id,
        'user_id': prompt_version.user_id,
        'version': prompt_version.version,
        'operative': prompt_version.operative,
        'original_prompt': prompt_version.original_prompt,
        'prompt_text': prompt_version.prompt_text,
        'created_at': prompt_version.created_at.isoformat(),  # Convert datetime to ISO string
        'updated_at': prompt_version.updated_at.isoformat()  # Convert datetime to ISO string
    }

def prompt_version_list_to_dict(prompt_versions: list[PromptVersion]):
    """
    Helper function to convert a list of PromptVersion objects to a list of dictionaries.
    """
    return [prompt_version_to_dict(pv) for pv in prompt_versions]


@prompt_bp.route('/', methods=['POST'])
def create_new_prompt():
    db = get_db()
    data = request.get_json()
    user_id = data.get('user_id')
    original_prompt = data.get('original_prompt')
    prompt_text = data.get('prompt_text')
    if not all([user_id, original_prompt, prompt_text]):
        return jsonify({"error": "Missing required fields"}), 400
    prompt_version = create_prompt_version(db, user_id=user_id, original_prompt=original_prompt, prompt_text=prompt_text)
    return jsonify(prompt_version_to_dict(prompt_version)), 201

@prompt_bp.route('/<int:prompt_version_id>', methods=['GET'])
def get_existing_prompt_version(prompt_version_id):
    db = get_db()
    prompt_version = get_prompt_version(db, prompt_version_id=prompt_version_id)
    if prompt_version:
        return jsonify(prompt_version_to_dict(prompt_version)), 200
    return jsonify({"error": "Prompt version not found"}), 404

@prompt_bp.route('/prompt_id/<int:prompt_id>', methods=['GET'])
def get_versions_by_prompt_id(prompt_id):
    db = get_db()
    prompt_versions = get_prompt_versions_by_prompt_id(db, prompt_id=prompt_id)
    return jsonify(prompt_version_list_to_dict(prompt_versions)), 200

@prompt_bp.route('/operative', methods=['GET'])
def get_all_operative_prompts():
    db = get_db()
    operative_prompts = get_operative_prompts(db)
    return jsonify(prompt_version_list_to_dict(operative_prompts)), 200

@prompt_bp.route('/<int:prompt_version_id>', methods=['PUT'])
def update_existing_prompt_version(prompt_version_id):
    db = get_db()
    prompt_version_to_update = get_prompt_version(db, prompt_version_id=prompt_version_id)
    if not prompt_version_to_update:
        return jsonify({"error": "Prompt version not found"}), 404
    data = request.get_json()
    user_id = data.get('user_id')
    prompt_text = data.get('prompt_text')
    if not all([user_id, prompt_text]):
        return jsonify({"error": "Missing required fields for update"}), 400
    updated_prompt_version = update_prompt_version(db, prompt_version_id=prompt_version_id, user_id=user_id, prompt_text=prompt_text)
    return jsonify(prompt_version_to_dict(updated_prompt_version)), 200

@prompt_bp.route('/<int:prompt_version_id>', methods=['DELETE'])
def delete_existing_prompt_version(prompt_version_id):
    db = get_db()
    if delete_prompt_version(db, prompt_version_id=prompt_version_id):
        return jsonify({"message": "Prompt version deleted successfully"}), 200
    return jsonify({"error": "Prompt version not found"}), 404
