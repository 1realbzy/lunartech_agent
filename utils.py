#!/usr/bin/env python3
"""
Utility functions for LunarTech AI Interview Agent
"""

import sqlite3
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any
from config import DATABASE_FILE, DATA_DIR

def view_interview_data(interview_id: str = None) -> None:
    """View interview data from the database."""
    try:
        db_path = Path(DATABASE_FILE)
        if not db_path.exists():
            print("❌ No database found. Run an interview first.")
            return
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        if interview_id:
            # View specific interview
            cursor.execute("""
                SELECT i.id, i.timestamp, i.summary, e.name, e.interest_level, e.readiness, e.background
                FROM interviews i
                LEFT JOIN extracted_info e ON i.id = e.interview_id
                WHERE i.id = ?
            """, (interview_id,))
            
            result = cursor.fetchone()
            if result:
                print(f"\n📋 Interview Details for {interview_id}")
                print(f"Timestamp: {result[1]}")
                print(f"Candidate: {result[3] or 'Unknown'}")
                print(f"Interest Level: {result[4] or 'Unknown'}")
                print(f"Readiness: {result[5] or 'Unknown'}")
                print(f"Background: {result[6] or 'Unknown'}")
                print(f"\nSummary:\n{result[2] or 'No summary available'}")
                
                # Get Q&A pairs
                cursor.execute("""
                    SELECT question_number, question, answer
                    FROM questions_answers
                    WHERE interview_id = ?
                    ORDER BY question_number
                """, (interview_id,))
                
                qa_pairs = cursor.fetchall()
                if qa_pairs:
                    print("\n📝 Questions & Answers:")
                    for q_num, question, answer in qa_pairs:
                        print(f"\nQ{q_num}: {question}")
                        print(f"A{q_num}: {answer}")
            else:
                print(f"❌ Interview {interview_id} not found.")
        else:
            # List all interviews
            cursor.execute("""
                SELECT i.id, i.timestamp, e.name, e.interest_level
                FROM interviews i
                LEFT JOIN extracted_info e ON i.id = e.interview_id
                ORDER BY i.timestamp DESC
            """)
            
            results = cursor.fetchall()
            if results:
                print("\n📊 All Interviews:")
                print("-" * 80)
                print(f"{'ID':<15} {'Timestamp':<20} {'Name':<20} {'Interest':<10}")
                print("-" * 80)
                for interview_id, timestamp, name, interest in results:
                    print(f"{interview_id:<15} {timestamp:<20} {name or 'Unknown':<20} {interest or 'Unknown':<10}")
            else:
                print("❌ No interviews found in database.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

def export_interviews_to_json(output_file: str = "interviews_export.json") -> None:
    """Export all interview data to JSON file."""
    try:
        db_path = Path(DATABASE_FILE)
        if not db_path.exists():
            print("❌ No database found.")
            return
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all interviews with extracted info
        cursor.execute("""
            SELECT i.id, i.timestamp, i.summary, e.name, e.interest_level, e.readiness, e.background
            FROM interviews i
            LEFT JOIN extracted_info e ON i.id = e.interview_id
            ORDER BY i.timestamp
        """)
        
        interviews = []
        for row in cursor.fetchall():
            interview_id, timestamp, summary, name, interest, readiness, background = row
            
            # Get Q&A pairs for this interview
            cursor.execute("""
                SELECT question_number, question, answer
                FROM questions_answers
                WHERE interview_id = ?
                ORDER BY question_number
            """, (interview_id,))
            
            qa_pairs = cursor.fetchall()
            
            interview_data = {
                "id": interview_id,
                "timestamp": timestamp,
                "summary": summary,
                "extracted_info": {
                    "name": name,
                    "interest_level": interest,
                    "readiness": readiness,
                    "background": background
                },
                "questions_answers": [
                    {
                        "question_number": q_num,
                        "question": question,
                        "answer": answer
                    }
                    for q_num, question, answer in qa_pairs
                ]
            }
            interviews.append(interview_data)
        
        conn.close()
        
        # Export to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(interviews, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(interviews)} interviews to {output_file}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def clear_database() -> None:
    """Clear all interview data from database (use with caution!)."""
    try:
        db_path = Path(DATABASE_FILE)
        if not db_path.exists():
            print("❌ No database found.")
            return
        
        response = input("⚠️  Are you sure you want to delete ALL interview data? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM questions_answers")
        cursor.execute("DELETE FROM extracted_info")
        cursor.execute("DELETE FROM interviews")
        
        conn.commit()
        conn.close()
        
        print("✅ Database cleared successfully.")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

def test_audio_devices() -> None:
    """Test available audio devices."""
    try:
        import pyaudio
        
        audio = pyaudio.PyAudio()
        
        print("🎤 Available Audio Input Devices:")
        print("-" * 50)
        
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Device {i}: {device_info['name']}")
                print(f"  - Channels: {device_info['maxInputChannels']}")
                print(f"  - Sample Rate: {device_info['defaultSampleRate']}")
                print()
        
        audio.terminate()
        
    except Exception as e:
        print(f"❌ Error testing audio devices: {e}")

def main():
    """Main utility function with command-line interface."""
    import sys
    
    if len(sys.argv) < 2:
        print("🛠️  LunarTech Interview Agent Utilities")
        print("\nUsage:")
        print("  python utils.py list                    - List all interviews")
        print("  python utils.py view <interview_id>     - View specific interview")
        print("  python utils.py export [filename]       - Export interviews to JSON")
        print("  python utils.py clear                   - Clear all interview data")
        print("  python utils.py audio                   - Test audio devices")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        view_interview_data()
    elif command == "view":
        if len(sys.argv) < 3:
            print("❌ Please provide an interview ID")
            return
        view_interview_data(sys.argv[2])
    elif command == "export":
        filename = sys.argv[2] if len(sys.argv) > 2 else "interviews_export.json"
        export_interviews_to_json(filename)
    elif command == "clear":
        clear_database()
    elif command == "audio":
        test_audio_devices()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()