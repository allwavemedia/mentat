from pathlib import Path
from textwrap import dedent

import pytest

from mentat.session import Session
from tests.conftest import ConfigManager


@pytest.fixture(autouse=True)
def replacement_parser(mocker):
    mock_method = mocker.MagicMock()
    mocker.patch.object(ConfigManager, "parser", new=mock_method)
    mock_method.return_value = "replacement"


@pytest.mark.asyncio
async def test_insert(mock_call_llm_api, mock_collect_user_input, mock_setup_api_key):
    temp_file_name = "temp.py"
    with open(temp_file_name, "w") as f:
        f.write(dedent("""\
            # This is a temporary file
            # with 2 lines"""))

    mock_collect_user_input.set_stream_messages(
        [
            "",
            "y",
            "q",
        ]
    )
    mock_call_llm_api.set_generator_values([dedent(f"""\
        Conversation

        @ {temp_file_name} insert_line=2
        # I inserted this comment
        @""")])

    session = await Session.create([temp_file_name])
    await session.start()
    await session.stream.stop()
    with open(temp_file_name, "r") as f:
        content = f.read()
        expected_content = dedent("""\
            # This is a temporary file
            # I inserted this comment
            # with 2 lines""")
    assert content == expected_content


@pytest.mark.asyncio
async def test_delete(mock_call_llm_api, mock_collect_user_input, mock_setup_api_key):
    temp_file_name = "temp.py"
    with open(temp_file_name, "w") as f:
        f.write(dedent("""\
            # This is a temporary file
            # with 2 lines"""))

    mock_collect_user_input.set_stream_messages(
        [
            "",
            "y",
            "q",
        ]
    )
    mock_call_llm_api.set_generator_values([dedent(f"""\
        Conversation

        @ {temp_file_name} starting_line=1 ending_line=1
        @""")])

    session = await Session.create([temp_file_name])
    await session.start()
    await session.stream.stop()
    with open(temp_file_name, "r") as f:
        content = f.read()
        expected_content = dedent("""\
            # with 2 lines""")
    assert content == expected_content


@pytest.mark.asyncio
async def test_replace(mock_call_llm_api, mock_collect_user_input, mock_setup_api_key):
    temp_file_name = "temp.py"
    with open(temp_file_name, "w") as f:
        f.write(dedent("""\
            # This is a temporary file
            # with 2 lines"""))

    mock_collect_user_input.set_stream_messages(
        [
            "",
            "y",
            "q",
        ]
    )
    mock_call_llm_api.set_generator_values([dedent(f"""\
        Conversation

        @ {temp_file_name} starting_line=2 ending_line=2
        # I inserted this comment
        @""")])

    session = await Session.create([temp_file_name])
    await session.start()
    await session.stream.stop()
    with open(temp_file_name, "r") as f:
        content = f.read()
        expected_content = dedent("""\
            # This is a temporary file
            # I inserted this comment""")
    assert content == expected_content


@pytest.mark.asyncio
async def test_create_file(
    mock_call_llm_api, mock_collect_user_input, mock_setup_api_key
):
    temp_file_name = "temp.py"
    mock_collect_user_input.set_stream_messages(
        [
            "",
            "y",
            "q",
        ]
    )
    mock_call_llm_api.set_generator_values([dedent(f"""\
        Conversation

        @ {temp_file_name} +
        @ {temp_file_name} insert_line=1
        # New line
        @""")])

    session = await Session.create([temp_file_name])
    await session.start()
    await session.stream.stop()
    with open(temp_file_name, "r") as f:
        content = f.read()
        expected_content = dedent("""\
            # New line""")
    assert content == expected_content


@pytest.mark.asyncio
async def test_delete_file(
    mock_call_llm_api, mock_collect_user_input, mock_setup_api_key
):
    temp_file_name = "temp.py"
    with open(temp_file_name, "w") as f:
        f.write(dedent("""\
            # This is a temporary file
            # with 2 lines"""))

    mock_collect_user_input.set_stream_messages(
        [
            "",
            "y",
            "y",
            "q",
        ]
    )
    mock_call_llm_api.set_generator_values([dedent(f"""\
        Conversation

        @ {temp_file_name} -""")])

    session = await Session.create([temp_file_name])
    await session.start()
    await session.stream.stop()
    assert not Path(temp_file_name).exists()


@pytest.mark.asyncio
async def test_rename_file(
    mock_call_llm_api, mock_collect_user_input, mock_setup_api_key
):
    temp_file_name = "temp.py"
    temp_file_name_2 = "temp2.py"
    with open(temp_file_name, "w") as f:
        f.write(dedent("""\
            # This is a temporary file
            # with 2 lines"""))

    mock_collect_user_input.set_stream_messages(
        [
            "",
            "y",
            "q",
        ]
    )
    mock_call_llm_api.set_generator_values([dedent(f"""\
        Conversation

        @ {temp_file_name} {temp_file_name_2}""")])

    session = await Session.create([temp_file_name])
    await session.start()
    await session.stream.stop()
    assert not Path(temp_file_name).exists()
    with open(temp_file_name_2, "r") as f:
        content = f.read()
        expected_content = dedent("""\
            # This is a temporary file
            # with 2 lines""")
    assert content == expected_content


@pytest.mark.asyncio
async def test_change_then_rename_then_change(
    mock_call_llm_api, mock_collect_user_input, mock_setup_api_key
):
    temp_file_name = "temp.py"
    temp_file_name_2 = "temp2.py"
    with open(temp_file_name, "w") as f:
        f.write(dedent("""\
            # This is a temporary file
            # with 2 lines"""))

    mock_collect_user_input.set_stream_messages(
        [
            "",
            "y",
            "q",
        ]
    )
    mock_call_llm_api.set_generator_values([dedent(f"""\
        Conversation
        
        @ {temp_file_name} starting_line=1 ending_line=1
        # New line 1
        @
        @ {temp_file_name} {temp_file_name_2}
        @ {temp_file_name_2} insert_line=2
        # New line 2
        @""")])

    session = await Session.create([temp_file_name])
    await session.start()
    await session.stream.stop()
    assert not Path(temp_file_name).exists()
    with open(temp_file_name_2, "r") as f:
        content = f.read()
        expected_content = dedent("""\
            # New line 1
            # New line 2
            # with 2 lines""")
    assert content == expected_content