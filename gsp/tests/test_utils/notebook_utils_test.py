from gsp.utils.notebook_utils import show


def test_show_displays_single_objects():
    # --- SETUP ---
    obj = "hello"

    # --- ACT ---
    show(obj)

    # --- ASSERT ---
    # No need to assert anything, just check if the object is displayed in the notebook
    assert True


def test_show_dispalys_multiple_objects():
    # --- SETUP ---
    obj1 = "hello"
    obj2 = "world"

    # --- ACT ---
    show(obj1, obj2)

    # --- ASSERT ---
    # No need to assert anything, just check if the objects are displayed in the notebook
    assert True
