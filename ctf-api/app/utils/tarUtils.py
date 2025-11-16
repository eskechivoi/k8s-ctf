import os
import tarfile
import shutil
from pathlib import Path
from flask import current_app as app

def save_chart(chart_file_stream, charts_storage_dir):
    """
    Saves a Chart file stream, extracts it, handles the internal folder,
    renames the folder to the Chart.name, and returns the final path.
    
    :param chart_file_stream: The file object from request.files
    :param charts_storage_dir: The target directory (e.g., /app/charts)
    :return: The full path to the extracted chart directory (charts_storage_dir/safe_name).
    """
    
    Path(charts_storage_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Save the file temporarily
    uploaded_file_path = os.path.join('/tmp', 'temp_chart.tgz')
    
    try:
        chart_file_stream.save(uploaded_file_path)

        temp_extract_dir = os.path.join(charts_storage_dir, f'temp_extract_chart')
        if Path(temp_extract_dir).exists():
             shutil.rmtree(temp_extract_dir)
        Path(temp_extract_dir).mkdir(parents=True, exist_ok=True)

        # 2. Extract the file into the temporary location
        with tarfile.open(uploaded_file_path, 'r:*') as tar:
            tar.extractall(path=temp_extract_dir)

        # 3. Find the actual root folder name inside the extracted content
        extracted_content = os.listdir(temp_extract_dir)
        
        chart_root_folders = [
            f for f in extracted_content if os.path.isdir(os.path.join(temp_extract_dir, f))
        ]

        if not chart_root_folders or len(chart_root_folders) != 1:
            raise tarfile.TarError(
                "Extracted content does not contain a single root chart directory."
            )

        chart_root_folder_name = chart_root_folders[0]
        original_chart_path = os.path.join(temp_extract_dir, chart_root_folder_name)

        # 4. Define the final, desired path
        name_parts = chart_root_folder_name.rsplit('-', 1)    
        if len(name_parts) > 1 and any(c.isdigit() for c in name_parts[1]):
            final_chart_name = name_parts[0]
        else:
            final_chart_name = chart_root_folder_name
        final_chart_dir = os.path.join(charts_storage_dir, final_chart_name)
        
        # 5. Clean up old directory if it exists
        if Path(final_chart_dir).exists():
            shutil.rmtree(final_chart_dir)

        # 6. Move/Rename the actual chart content to the final, standardized path
        shutil.move(original_chart_path, final_chart_dir)
        app.logger.info(f"Chart extracted to: {final_chart_dir}")

        # 7. Clean up the temporary directory
        shutil.rmtree(temp_extract_dir)

        return final_chart_dir
        
    except Exception as e:
        app.logger.error(f"Error in save_chart: {e}")
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
        raise e
    finally:
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)