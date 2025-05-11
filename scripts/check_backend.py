import os
import sys

def print_directory_structure(path, indent=0):
    """Print the directory structure starting from the given path."""
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return
    
    print(" " * indent + os.path.basename(path) + "/")
    
    try:
        items = os.listdir(path)
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                print_directory_structure(item_path, indent + 2)
            else:
                print(" " * (indent + 2) + item)
    except PermissionError:
        print(" " * (indent + 2) + "Permission denied")

def find_file_with_content(path, search_term):
    """Find files containing the specified search term."""
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return
    
    found_files = []
    
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):  # Only search Python files
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if search_term in content:
                                found_files.append(file_path)
                                print(f"Found '{search_term}' in: {file_path}")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    except Exception as e:
        print(f"Error walking directory {path}: {e}")
    
    return found_files

def print_file_content(file_path):
    """Print the content of a file."""
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n--- Content of {file_path} ---\n")
            print(content)
            print(f"\n--- End of {file_path} ---\n")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    backend_path = r"c:\users\betty\flask-akademiaKupula"
    
    print("\n=== Directory Structure ===\n")
    print_directory_structure(backend_path)
    
    print("\n=== Finding Contact Endpoint ===\n")
    contact_files = find_file_with_content(backend_path, "/api/contacto")
    
    if contact_files:
        for file_path in contact_files:
            print_file_content(file_path)
    else:
        print("No files found containing '/api/contacto'")
        
        # Try alternative search terms
        print("\n=== Searching for alternative contact endpoints ===\n")
        find_file_with_content(backend_path, "contacto")
        find_file_with_content(backend_path, "contact")
