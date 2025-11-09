import os
import tarfile
import shutil
from pathlib import Path

def save_chart(chart_file, charts_storage_dir, safe_name):
    # Save and uncompress the file
    chart_dir = os.path.join(charts_storage_dir, safe_name)
    uploaded_file_path = os.path.join('/tmp', f'{safe_name}.tgz')
    chart_file.save(uploaded_file_path)
    
    if Path(chart_dir).exists():
        shutil.rmtree(chart_dir)
        
    Path(charts_storage_dir).mkdir(exist_ok=True)

    with tarfile.open(uploaded_file_path, 'r:gz') as tar:
        tar.extractall(path=charts_storage_dir)