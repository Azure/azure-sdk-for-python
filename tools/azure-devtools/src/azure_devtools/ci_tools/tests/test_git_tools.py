from pathlib import Path
import tempfile

from git import Repo

from azure_devtools.ci_tools.git_tools import (
    do_commit,
    get_files_in_commit
)

def test_do_commit():
    finished = False # Authorize PermissionError on cleanup
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            Repo.clone_from('https://github.com/lmazuel/TestingRepo.git', temp_dir)
            repo = Repo(temp_dir)

            result = do_commit(repo, 'Test {hexsha}', 'testing', 'fakehexsha')
            assert not result
            assert 'fakehexsha' not in repo.head.commit.message
            assert repo.active_branch.name == 'master'

            file_path = Path(temp_dir, 'file.txt')
            file_path.write_text('Something')

            result = do_commit(repo, 'Test {hexsha}', 'testing', 'fakehexsha')
            assert result
            assert repo.head.commit.message == 'Test fakehexsha'
            assert repo.active_branch.name == 'testing'
            assert 'file.txt' in repo.head.commit.stats.files

            file_path.write_text('New content')

            result = do_commit(repo, 'Now it is {hexsha}', 'newbranch', 'new-fakehexsha')
            assert result
            assert repo.head.commit.message == 'Now it is new-fakehexsha'
            assert repo.active_branch.name == 'newbranch'
            assert 'file.txt' in repo.head.commit.stats.files

            file_path.unlink()
            file_path.write_text('New content')

            result = do_commit(repo, 'Now it is {hexsha}', 'fakebranch', 'hexsha_not_used')
            assert not result
            assert repo.head.commit.message == 'Now it is new-fakehexsha'
            assert repo.active_branch.name == 'newbranch'

            finished = True
    except PermissionError:
        if finished:
            return
        raise

def test_get_files_in_commit():
    finished = False # Authorize PermissionError on cleanup
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            Repo.clone_from('https://github.com/lmazuel/swagger-to-sdk.git', temp_dir)
            
            files = get_files_in_commit(temp_dir, "b40451e55b26e3db61ea17bd751181cbf91f60c5")

            assert files == [
                'swaggertosdk/generate_package.py',
                'swaggertosdk/python_sdk_tools.py',
                'swaggertosdk/restapi/sdkbot.py'
            ]

            finished = True
    except PermissionError:
        if finished:
            return
        raise
