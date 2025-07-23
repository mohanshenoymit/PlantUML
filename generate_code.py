import re
import os

def generate_java_code_from_plantuml(plantuml_content, output_dir="generated_java"):
    """
    Generates basic Java class and interface files from PlantUML class diagram content.

    Args:
        plantuml_content (str): The raw PlantUML class diagram text.
        output_dir (str): The directory where generated Java files will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating Java code into: {os.path.abspath(output_dir)}")

    # Regular expressions to find classes, abstract classes, and interfaces
    class_pattern = re.compile(r'(?:(abstract)\s+)?class\s+(\w+)\s*\{([^}]*)\}', re.DOTALL)
    interface_pattern = re.compile(r'interface\s+(\w+)\s*\{([^}]*)\}', re.DOTALL)

    # Regular expressions to find attributes and methods within class/interface bodies
    member_pattern = re.compile(r'^\s*([+\-#~])\s*(\w+)(?:\s*:\s*(\w+))?(?:\(([^)]*)\))?(?:\s*:\s*(\w+))?$', re.MULTILINE)

    # Regular expressions to find relationships (inheritance, implementation)
    inheritance_pattern = re.compile(r'(\w+)\s*<\|--\s*(\w+)') # Child <|-- Parent
    implementation_pattern = re.compile(r'(\w+)\s*\.\.\|>\s*(\w+)') # Class ..|> Interface

    # Store parsed classes/interfaces and their details
    parsed_elements = {}
    relationships = {'extends': {}, 'implements': {}}

    # --- Pass 1: Parse Classes and Interfaces ---
    for match in class_pattern.finditer(plantuml_content):
        is_abstract, name, body = match.groups()
        parsed_elements[name] = {
            'type': 'abstract_class' if is_abstract else 'class',
            'attributes': [],
            'methods': [],
            'body': body # Store body for later parsing of members
        }

    for match in interface_pattern.finditer(plantuml_content):
        name, body = match = match.groups()
        parsed_elements[name] = {
            'type': 'interface',
            'attributes': [], # Interfaces don't have attributes in Java/C#
            'methods': [],
            'body': body
        }

    # --- Pass 2: Parse Members (Attributes and Methods) ---
    for name, details in parsed_elements.items():
        for line in details['body'].split('\n'):
            member_match = member_pattern.match(line.strip())
            if member_match:
                visibility_char, member_name, attr_type, params_str, return_type = member_match.groups()

                java_visibility = {
                    '+': 'public',
                    '-': 'private',
                    '#': 'protected',
                    '~': '' # Package-private, default in Java
                }.get(visibility_char, 'public') # Default to public if unknown

                if params_str is not None: # It's a method
                    params = []
                    if params_str:
                        for p in params_str.split(','):
                            p_parts = p.strip().split(':')
                            if len(p_parts) == 2:
                                params.append(f"{p_parts[1].strip()} {p_parts[0].strip()}")
                            else:
                                params.append(p.strip()) # Fallback for malformed params
                    java_return_type = return_type if return_type else 'void'
                    details['methods'].append({
                        'visibility': java_visibility,
                        'name': member_name,
                        'parameters': ", ".join(params),
                        'return_type': java_return_type
                    })
                else: # It's an attribute
                    java_attr_type = attr_type if attr_type else 'Object' # Default to Object if type not specified
                    details['attributes'].append({
                        'visibility': java_visibility,
                        'type': java_attr_type,
                        'name': member_name
                    })

    # --- Pass 3: Parse Relationships ---
    for match in inheritance_pattern.finditer(plantuml_content):
        child, parent = match.groups()
        if child in parsed_elements and parent in parsed_elements:
            relationships['extends'][child] = parent

    for match in implementation_pattern.finditer(plantuml_content):
        implementing_class, interface = match.groups()
        if implementing_class in parsed_elements and interface in parsed_elements:
            if implementing_class not in relationships['implements']:
                relationships['implements'][implementing_class] = []
            relationships['implements'][implementing_class].append(interface)

    # --- Pass 4: Generate Java Files ---
    for name, details in parsed_elements.items():
        file_name = os.path.join(output_dir, f"{name}.java")
        with open(file_name, 'w') as f:
            # Package declaration (optional, can be added if needed)
            # f.write("package com.university.model;\n\n")

            # Imports (basic Date and List for common types)
            if any(attr['type'] == 'Date' for attr in details['attributes']) or \
               any('Date' in m['parameters'] or 'Date' in m['return_type'] for m in details['methods']):
                f.write("import java.util.Date;\n")
            if any('List' in attr['type'] for attr in details['attributes']) or \
               any('List' in m['parameters'] or 'List' in m['return_type'] for m in details['methods']):
                f.write("import java.util.List;\n")
                f.write("import java.util.ArrayList;\n")
            if f.tell() > 0: # Add newline if imports were written
                f.write("\n")

            # Class/Interface declaration
            declaration_line = ""
            if details['type'] == 'abstract_class':
                declaration_line = f"public abstract class {name}"
            elif details['type'] == 'class':
                declaration_line = f"public class {name}"
            elif details['type'] == 'interface':
                declaration_line = f"public interface {name}"

            # Add extends clause
            if name in relationships['extends']:
                declaration_line += f" extends {relationships['extends'][name]}"

            # Add implements clause
            if name in relationships['implements']:
                interfaces = ", ".join(relationships['implements'][name])
                declaration_line += f" implements {interfaces}"

            f.write(f"{declaration_line} {{\n")

            # Attributes
            for attr in details['attributes']:
                f.write(f"    {attr['visibility']} {attr['type']} {attr['name']};\n")
            if details['attributes']:
                f.write("\n") # Add newline after attributes if any

            # Constructor (basic, only for classes, not interfaces)
            if details['type'] != 'interface':
                # Simple constructor with all attributes as parameters
                constructor_params = []
                for attr in details['attributes']:
                    constructor_params.append(f"{attr['type']} {attr['name']}")
                
                # If extending a class, add parent constructor parameters (heuristic)
                parent_class = relationships['extends'].get(name)
                if parent_class and parent_class in parsed_elements and parsed_elements[parent_class]['type'] != 'interface':
                    parent_attrs = parsed_elements[parent_class]['attributes']
                    parent_constructor_params = [f"{attr['type']} {attr['name']}" for attr in parent_attrs]
                    constructor_params = parent_constructor_params + constructor_params
                    
                    # Add super() call
                    super_call_params = [attr['name'] for attr in parent_attrs]
                    if super_call_params:
                        f.write(f"    public {name}({', '.join(constructor_params)}) {{\n")
                        f.write(f"        super({', '.join(super_call_params)});\n")
                        for attr in details['attributes']:
                            f.write(f"        this.{attr['name']} = {attr['name']};\n")
                        f.write("    }\n\n")
                    else:
                        f.write(f"    public {name}({', '.join(constructor_params)}) {{\n")
                        for attr in details['attributes']:
                            f.write(f"        this.{attr['name']} = {attr['name']};\n")
                        f.write("    }\n\n")
                else:
                    f.write(f"    public {name}({', '.join(constructor_params)}) {{\n")
                    for attr in details['attributes']:
                        f.write(f"        this.{attr['name']} = {attr['name']};\n")
                    f.write("    }\n\n")


            # Getters and Setters (for private attributes)
            for attr in details['attributes']:
                if attr['visibility'] == 'private':
                    # Getter
                    f.write(f"    public {attr['type']} get{attr['name'].capitalize()}() {{\n")
                    f.write(f"        return {attr['name']};\n")
                    f.write("    }\n\n")
                    # Setter
                    f.write(f"    public void set{attr['name'].capitalize()}({attr['type']} {attr['name']}) {{\n")
                    f.write(f"        this.{attr['name']} = {attr['name']};\n")
                    f.write("    }\n\n")

            # Methods
            for method in details['methods']:
                method_modifier = ""
                if details['type'] == 'abstract_class' and method['visibility'] == 'public' and 'abstract' in method['name'].lower():
                    method_modifier = "abstract "
                    method['name'] = method['name'].replace('{abstract}', '').strip() # Remove {abstract} from name
                elif details['type'] == 'interface':
                    # Methods in interfaces are implicitly public and abstract in Java 8+
                    method_modifier = ""
                    method['visibility'] = "public" # Ensure public for interface methods
                    
                # Handle static methods
                if '{static}' in method['name'].lower():
                    method_modifier += "static "
                    method['name'] = method['name'].replace('{static}', '').strip()

                f.write(f"    {method['visibility']} {method_modifier}{method['return_type']} {method['name']}({method['parameters']})")
                if details['type'] == 'interface' or method_modifier.strip() == 'abstract':
                    f.write(";\n\n") # Abstract methods and interface methods end with semicolon
                else:
                    f.write(" {\n")
                    f.write("        // TODO: Implement method logic\n")
                    if method['return_type'] != 'void':
                        f.write(f"        return default{method['return_type']}Value(); // Placeholder return\n")
                    f.write("    }\n\n")

            f.write("}\n")
            print(f"Generated {name}.java")

# Helper function for placeholder return values
def default_return_value(java_type):
    if java_type == 'int' or java_type == 'long' or java_type == 'short' or java_type == 'byte':
        return '0'
    elif java_type == 'double' or java_type == 'float':
        return '0.0'
    elif java_type == 'boolean':
        return 'false'
    elif java_type == 'char':
        return "'\\0'"
    else:
        return 'null'

# Add this to the end of your script to make it runnable
if __name__ == "__main__":
    plantuml_file_path = "university_diagram.puml" # Change this to your PlantUML file name

    # Create a dummy PlantUML file for demonstration if it doesn't exist
    if not os.path.exists(plantuml_file_path):
        print(f"Creating a sample PlantUML file: {plantuml_file_path}")
        sample_plantuml_content = """
@startuml
title University System Class Diagram

skinparam classAttributeIconSize 0

' Abstract Class
abstract class Person {
  - name: String
  - dob: Date
  + {abstract} getAge(): int
  + getDetails(): String
}

' Concrete Classes
class Student {
  - studentId: String
  - major: String
  + Student(name: String, dob: Date, studentId: String)
  + enrollCourse(course: Course): void
  + getStudentId(): String
}

class Professor {
  - employeeId: String
  - department: String
  + teachCourse(course: Course): void
  + assignGrade(student: Student, course: Course, grade: String): void
}

class Course {
  - courseId: String
  - title: String
  - credits: int
  + getCourseTitle(): String
  + {static} getCreditHours(): int
}

' Interface
interface Payable {
  + calculateSalary(): double
  + payTax(amount: double): void
}

' Relationships
' Inheritance: Professor and Student are a type of Person
Person <|-- Student
Person <|-- Professor

' Association: Professor teaches a Course
Professor "1" o-- "0..*" Course : teaches >

' Aggregation: A Course has multiple Students
Course "1" o-- "0..*" Student : enrolledStudents >

' Realization (Interface Implementation): A Professor is Payable
Professor ..|> Payable

' Dependency: A Professor uses Student and Course in a method but doesn't own them
Professor .> Student
Professor .> Course

@enduml
"""
        with open(plantuml_file_path, "w") as f:
            f.write(sample_plantuml_content)

    with open(plantuml_file_path, "r") as f:
        plantuml_diagram = f.read()

    generate_java_code_from_plantuml(plantuml_diagram)
    print("\nCode generation complete. Check the 'generated_java' directory.")

