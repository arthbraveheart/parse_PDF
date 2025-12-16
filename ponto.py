#!/usr/bin/env python3
"""
Work Attendance PDF Processor
Extracts work days data from PDF ponto (attendance) files
"""

from pathlib import Path
import re
from datetime import datetime
import json
from typing import List, Tuple, Dict, Any
import pandas as pd
from pypdf import PdfReader
import logging
from tqdm import tqdm  # pip install tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AttendanceExtractor:
    """Extracts attendance data from PDF ponto files"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.exclude_folders = {'temp', 'old', 'backup'}  # Folders to skip
        
    def extract_worked_days(self, lines: List[str]) -> Tuple[str, int]:
        """
        Extract period and count of worked days from text lines
        
        Args:
            lines: List of text lines from PDF page
            
        Returns:
            Tuple of (period, days_worked)
        """
        iterator = iter(lines)
        days_count = 0
        
        # Find the attendance table
        for line in iterator:
            if 'Matricula' in line:
                # We're in the right section, start counting
                line = next(iterator, '')
                while 'Historico' not in line:
                    # Each day entry seems to have colons in the time stamps
                    days_count += 1 if ':' in line else 0
                    line = next(iterator, '')
                break
        
        # Extract period (month/year) from header
        period_match = re.search(r"(\w+)\s*/\s*(\d+)", lines[3] if len(lines) > 3 else "")
        period = f"{period_match.group(1)}/{period_match.group(2)}" if period_match else "Unknown"
        
        logger.debug(f"Found period {period} with {days_count} worked days")
        return period, days_count
    
    def extract_employee_info(self, pdf_page_text: str) -> Dict[str, str]:
        """Extract employee name and registration number from PDF"""
        info = {}
        
        # Extract employee name
        name_match = re.search(r"Empregado\s*:\s*([^\n]+?)\s+Categoria", pdf_page_text)
        info['name'] = name_match.group(1).strip() if name_match else "Unknown"
        
        # Extract registration number (matrícula)
        reg_match = re.search(r"Matricula\s*:\s*([^\n]+)", pdf_page_text)
        info['registration'] = reg_match.group(1).strip() if reg_match else "Unknown"
        
        return info
    
    def process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Process a single PDF file and extract all attendance data"""
        logger.info(f"Processing: {pdf_path.name}")
        
        try:
            reader = PdfReader(str(pdf_path))
            if not reader.pages:
                logger.warning(f"No pages in {pdf_path.name}")
                return {}
            
            # Get employee info from first page
            first_page_text = reader.pages[0].extract_text()
            employee_info = self.extract_employee_info(first_page_text)
            
            # Process all pages for attendance data
            attendance_data = []
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                lines = page_text.split('\n')
                period, days = self.extract_worked_days(lines)
                attendance_data.append({
                    'period': period,
                    'days_worked': days,
                    'page': page_num
                })
            
            return {
                **employee_info,
                'file': pdf_path.name,
                'attendance': attendance_data,
                'total_days': sum(item['days_worked'] for item in attendance_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            return {}

def find_pdf_files(folder_path: Path) -> List[Path]:
    """Find all PDF files in directory and subdirectories"""
    pdf_files = []
    
    for pdf_path in folder_path.rglob("*.pdf"):
        # Skip files in excluded folders
        if not any(excluded in pdf_path.parts for excluded in ['temp', 'backup']):
            pdf_files.append(pdf_path)
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    return pdf_files

def export_to_excel(data: List[Dict], output_folder: Path):
    """Export processed data to Excel files"""
    output_folder.mkdir(exist_ok=True)
    
    for item in data:
        if not item or 'attendance' not in item:
            continue
        
        # Create DataFrame from attendance data
        df = pd.DataFrame(item['attendance'])
        
        # Create filename
        safe_name = re.sub(r'[^\w\s-]', '', item.get('name', 'Unknown')).strip()
        filename = f"{item.get('registration', '000')}_{safe_name}.xlsx"
        filepath = output_folder / filename
        
        # Save to Excel
        df.to_excel(filepath, index=False)
        logger.info(f"Exported: {filename}")

def main():
    """Main processing function"""
    # Configuration - update these paths as needed
    BASE_PATH = Path.home() / "Documents" / "Documentos Perito - final"
    OUTPUT_FOLDER = Path.home() / "Documents" / "Attendance_Reports"
    
    # Add your custom exclusions here if needed
    EXCLUDE_INDICES = {151, 135, 2, 140, 133}
    
    logger.info("Starting PDF processing...")
    
    # Find all PDF files
    all_pdfs = find_pdf_files(BASE_PATH)
    
    if not all_pdfs:
        logger.error("No PDF files found!")
        return
    
    # Process all PDFs with progress bar
    all_data = []
    extractor = AttendanceExtractor(BASE_PATH)
    
    for pdf_path in tqdm(all_pdfs, desc="Processing PDFs"):
        data = extractor.process_pdf(pdf_path)
        if data:
            all_data.append(data)
    
    # Save all data to JSON
    json_file = OUTPUT_FOLDER / "attendance_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved data to {json_file}")
    
    # Export to Excel
    export_to_excel(all_data, OUTPUT_FOLDER)
    
    # Print summary
    logger.info(f"Processed {len(all_data)} PDF files")
    total_days = sum(item.get('total_days', 0) for item in all_data)
    logger.info(f"Total worked days: {total_days}")

if __name__ == "__main__":
    import time
    start_time = time.time()
    
    main()
    
    elapsed = time.time() - start_time
    logger.info(f"Processing completed in {elapsed:.2f} seconds")