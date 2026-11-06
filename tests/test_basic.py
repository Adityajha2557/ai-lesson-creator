from modules.database import init_db, save_project, load_project

def test_save_and_load():
    init_db()
    project_id = save_project("Test", "Objective", "Lesson", [], "", "")
    result = load_project(project_id)
    assert result["title"] == "Test"
    assert result["lesson"] == "Lesson"
