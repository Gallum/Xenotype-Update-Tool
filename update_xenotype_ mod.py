
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Compatibility adjustments for RimWorld 1.5
REQUIRED_ATTRIBUTES = {
    "graphicData": """<graphicData>
  <layer>PostHeadgear</layer>
  <drawNorthAfterHair>true</drawNorthAfterHair>
</graphicData>"""
}

CHANGES = {
    "<renderNodeProperties>": "<graphicData>",
    "</renderNodeProperties>": "</graphicData>",
    "<layer>80</layer>": "<layer>PostHeadgear</layer>",
    "<drawNorthAfterHair>false</drawNorthAfterHair>": "<drawNorthAfterHair>true</drawNorthAfterHair>",
}

def create_incremental_zip(root_dir, target_dirs, zip_prefix, log):
    """
    Create an incremental zip file for backups or diagnostics.
    """
    revision = 0
    while os.path.exists(os.path.join(root_dir, f"{zip_prefix} rev {revision:02}.zip")):
        revision += 1
    zip_name = f"{zip_prefix} rev {revision:02}.zip"
    zip_path = os.path.join(root_dir, zip_name)

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for folder in target_dirs:
                folder_path = os.path.join(root_dir, folder)
                if os.path.exists(folder_path):
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, root_dir)
                            zip_file.write(file_path, arcname)
            log.append(f"{zip_prefix} created successfully: {zip_path}")
    except Exception as e:
        log.append(f"Failed to create {zip_prefix} zip file: {e}")

    return zip_path

def create_initial_backup(root_dir, log):
    """
    Create an initial backup file (backup.zip) with a README for verification.
    """
    initial_backup_path = os.path.join(root_dir, "backup.zip")
    if os.path.exists(initial_backup_path):
        log.append("Initial backup already exists.")
        return

    try:
        with zipfile.ZipFile(initial_backup_path, "w", zipfile.ZIP_DEFLATED) as backup_zip:
            for folder in ["1.4", "About"]:
                folder_path = os.path.join(root_dir, folder)
                if os.path.exists(folder_path):
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, root_dir)
                            backup_zip.write(file_path, arcname)
            # Add README file for verification
            readme_path = os.path.join(root_dir, "README.txt")
            with open(readme_path, "w") as readme:
                readme.write("This is the initial backup zip file created for safety purposes.")
            backup_zip.write(readme_path, "README.txt")
            os.remove(readme_path)  # Clean up README file
            log.append("Initial backup (backup.zip) created successfully.")
    except Exception as e:
        log.append(f"Failed to create initial backup: {e}")

def prettify_and_save(tree, file_path):
    """
    Save the XML tree to a file with refined pretty formatting.
    """
    try:
        raw_str = ET.tostring(tree.getroot(), encoding="utf-8")
        parsed_str = minidom.parseString(raw_str).toprettyxml(indent="  ")

        # Refine formatting: Remove excessive blank lines
        refined_str = "\n".join([line for line in parsed_str.splitlines() if line.strip()])

        # Write the refined XML to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(refined_str + "\n")
    except Exception as e:
        raise RuntimeError(f"Failed to save refined XML for {file_path}: {e}")

def validate_and_repair(file_path, log):
    """
    Validate and attempt to repair malformed XML files.
    """
    try:
        tree = ET.parse(file_path)
        return tree
    except ET.ParseError as e:
        log.append(f"Parse error in {file_path}: {e}. Attempting repair...")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
            cleaned_content = "".join(line.strip() for line in content)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)
            tree = ET.parse(file_path)
            log.append(f"Repaired and parsed {file_path} successfully.")
            return tree
        except Exception as repair_error:
            log.append(f"Failed to repair {file_path}: {repair_error}")
            return None

def apply_changes_with_refined_formatting(file_path, log):
    """
    Apply compatibility changes to an XML file with refined formatting.
    """
    tree = validate_and_repair(file_path, log)
    if tree is None:
        log.append(f"Skipping file due to persistent errors: {file_path}")
        return

    try:
        root = tree.getroot()
        content_updated = False

        # Apply tag replacements
        for old, new in CHANGES.items():
            for elem in root.iter():
                if elem.text and old in elem.text:
                    elem.text = elem.text.replace(old, new)
                    log.append(f"Replaced '{old}' with '{new}' in {file_path}.")
                    content_updated = True

        # Add missing attributes
        for attr, value in REQUIRED_ATTRIBUTES.items():
            if root.find(f".//{attr}") is None:
                new_element = ET.fromstring(value)
                root.append(new_element)
                log.append(f"Added missing attribute '{attr}' in {file_path}.")
                content_updated = True

        if content_updated:
            prettify_and_save(tree, file_path)
    except Exception as e:
        log.append(f"Failed to apply changes to {file_path}: {e}")

def update_about_xml(root_dir, log):
    """
    Update About.xml to include RimWorld 1.5 in <supportedVersions>.
    """
    about_file_path = os.path.join(root_dir, "About", "About.xml")
    if not os.path.isfile(about_file_path):
        log.append("About.xml not found. Skipping update.")
        return

    try:
        tree = ET.parse(about_file_path)
        root = tree.getroot()

        supported_versions = root.find(".//supportedVersions")
        if supported_versions is None:
            supported_versions = ET.SubElement(root, "supportedVersions")
            log.append("<supportedVersions> tag created.")

        versions = [li.text for li in supported_versions.findall("li")]
        if "1.5" not in versions:
            new_version = ET.Element("li")
            new_version.text = "1.5"
            supported_versions.append(new_version)
            log.append("Added RimWorld 1.5 to <supportedVersions> in About.xml.")

        prettify_and_save(tree, about_file_path)
    except Exception as e:
        log.append(f"Failed to update About.xml: {e}")

def preprocess_and_update_full_backup(root_dir, version_from, version_to):
    """
    Update a mod from version 1.4 to 1.5 with integrated backup and results packaging.
    """
    src_dir = os.path.join(root_dir, version_from)
    dest_dir = os.path.join(root_dir, version_to)
    log = []

    try:
        # Step 1: Create the initial backup if it doesn't exist
        log.append("Checking for initial backup...")
        create_initial_backup(root_dir, log)

        # Step 2: Create an incremental backup
        log.append("Creating an incremental backup...")
        create_incremental_zip(root_dir, ["1.4", "About"], "backup", log)

        # Step 3: Preprocess files in the source directory
        log.append("Preprocessing XML files in the source directory...")
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    validate_and_repair(file_path, log)

        log.append("Preprocessing completed.")

        # Step 4: Copy files to the destination directory
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        log.append(f"Copied files from '{src_dir}' to '{dest_dir}'.")

        # Step 5: Apply updates to the copied files
        for root, _, files in os.walk(dest_dir):
            for file in files:
                if file.endswith(".xml"):
                    apply_changes_with_refined_formatting(os.path.join(root, file), log)

        # Step 6: Update About.xml
        update_about_xml(root_dir, log)

        # Step 7: Create a results zip
        log.append("Creating results package...")
        create_incremental_zip(root_dir, ["1.4", "About", version_to, f"{version_to}_update_log.txt"], "results", log)

        log.append("Update and packaging completed successfully.")
    except Exception as e:
        log.append(f"Error during update: {e}")
        shutil.rmtree(dest_dir, ignore_errors=True)
    finally:
        log_file = os.path.join(root_dir, f"{version_to}_update_log.txt")
        with open(log_file, "w", encoding="utf-8") as log_out:
            log_out.write("\n".join(log))

if __name__ == "__main__":
    ROOT_DIR = os.getcwd()
    VERSION_FROM = "1.4"
    VERSION_TO = "1.5"
    preprocess_and_update_full_backup(ROOT_DIR, VERSION_FROM, VERSION_TO)
