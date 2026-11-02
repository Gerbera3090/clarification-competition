import os
import subprocess
import uuid

try:
    import evalplus
    from evalplus.data import get_human_eval_plus, get_human_eval_plus_hash
    from evalplus.data.mbpp import get_mbpp_plus, get_mbpp_plus_hash
    from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS, MBPP_OUTPUT_SET_EQ_TASKS
    from evalplus.evaluate import get_groundtruth
except ImportError:
    evalplus = None


def _check_consistency(dataset, missing_entries):
    for example in dataset:
        if example["task_id"] not in missing_entries:
            continue

        target = missing_entries[example["task_id"]]
        assert example["entry_point"] == target["entry_point"], (
            f"[{example['task_id']}] the entry point does not match ({example['entry_point']} != {target['entry_point']})"
        )
        assert example.get("test_cases", None) == target.get("test_cases", None), (
            f"[{example['task_id']}] test cases doe not match."
        )


def init_evalplus_evaluator(dataset, train=False):
    if evalplus is None:
        raise ImportError("Install evalplus (`pip install evalplus`) to use the runtime evaluator.")

    dataset_ids = set(example["task_id"].split("/", 1)[0] for example in dataset)

    final_dataset = {}
    ground_truth = {}

    for dataset_id in dataset_ids:
        ds = {}
        gt = {}
        if dataset_id == "Mbpp":
            ds = get_mbpp_plus()
            hash = get_mbpp_plus_hash() + ("_train" if train else "")
            gt = get_groundtruth(ds, hash, MBPP_OUTPUT_NOT_NONE_TASKS)
        elif dataset_id == "HumanEval":
            ds = get_human_eval_plus()
            hash = get_human_eval_plus_hash() + ("_train" if train else "")
            gt = get_groundtruth(ds, hash, [])
        final_dataset.update(ds)
        ground_truth.update(gt)

    # There is no EvalPlus ground truth for MBPP train set examples (default to test cases).
    missing_entries = {
        example["task_id"]: example
        for example in dataset
        if example["task_id"] not in final_dataset
    }

    _check_consistency(dataset, missing_entries)
    final_dataset.update(missing_entries)
    # Keep EvalPlus inputs, expected outputs and oracle selection authoritative,
    # but call the entry point that was actually provided to the algorithm.
    # MBPP names can differ in capitalization between the two datasets.
    entry_points = {}
    for example in dataset:
        task_id, entry_point = example["task_id"], example["entry_point"]
        if task_id in entry_points and entry_points[task_id] != entry_point:
            raise ValueError(f"Problem {task_id} has conflicting entry points in the dataset.")
        entry_points[task_id] = entry_point
    return EvalPlusEvaluator(final_dataset, ground_truth, entry_points=entry_points)


class EvalPlusEvaluator:
    def __init__(self, problems, ground_truth, entry_points=None):
        self.problems = problems
        self.ground_truth = ground_truth
        self.entry_points = dict(entry_points or {})

    def partial(self, example):
        task_id = example["task_id"]

        try:
            problem = self.problems[task_id]
        except KeyError as e:
            raise ValueError(f"Problem {task_id} is unknown.") from e

        try:
            gt = self.ground_truth[task_id]
        except KeyError as e:
            if "test_cases" in problem:
                gt = problem["test_cases"]
            else:
                raise ValueError(f"Problem {task_id} does not have a ground truth.") from e

        return EvalPlusDockerInstanceEvaluator(
            problem, gt, entry_point=self.entry_points.get(task_id)
        )

    def evaluate(self, example, response):
        return self.partial(example).evaluate(example, response)


# Docker evaluator -------------------------------------------------------------------------------------

TEST_TRIGGER = """
import numpy as np 
from math import inf

def is_floats(x) -> bool: 
    # check if it is float; List[float]; Tuple[float] 
    if isinstance(x, float): 
        return True 
    if isinstance(x, (list, tuple)): 
        return len(x) > 0 and all(isinstance(i, float) for i in x) 
    if isinstance(x, np.ndarray): 
        return x.dtype == np.float64 or x.dtype == np.float32 
    return False

def assertion(out, exp, atol, inp): 
    if atol == 0 and is_floats(exp): 
        atol = 1e-6 
    
    if out != exp and atol != 0: 
        assert np.allclose(out, exp, rtol=1e-07, atol=atol), f"Failed for inputs \'{inp}\': Expected to be close to \'{exp}\', but got {out}"
    else: 
        assert {oracle}, f"Failed for inputs \'{inp}\': Expected \'{exp}\', but got {out}"
    
inputs = {inputs}
results = {results}
for i, (inp, exp) in enumerate(zip(inputs, results)):
    assertion({entry_point}(*inp), exp, {atol}, inp)
print("PASSED TESTS")
"""


class EvalPlusDockerInstanceEvaluator:
    def __init__(self, problem, ground_truth, entry_point=None):
        self.problem = problem
        self.ground_truth = ground_truth
        self.entry_point = problem["entry_point"] if entry_point is None else entry_point

    def _oracle(self):
        entry_point = self.problem["entry_point"]

        if "are_equivalent" == entry_point:  # Mbpp/164 special oracle
            return "out == exp or True"
        elif "sum_div" == entry_point:  # Mbpp/295 special oracle
            return "out == exp or out == 0"
        elif entry_point in MBPP_OUTPUT_SET_EQ_TASKS:
            return "set(out) == set(exp)"
        elif entry_point in MBPP_OUTPUT_NOT_NONE_TASKS:
            return "out == exp if isinstance(out, bool) else exp == (out is not None)"

        return "out == exp"

    def _construct_tests(self, test_trigger=TEST_TRIGGER):
        if not self.ground_truth:
            raise RuntimeError("The evaluator does not have access to the ground truth.")

        try:
            inputs = self.problem["base_input"] + list(self.problem["plus_input"])
            results = self.ground_truth["base"] + list(self.ground_truth["plus"])

            for key, value in [
                ("entry_point", self.entry_point),
                ("inputs", inputs),
                ("results", results),
                ("atol", self.problem.get("atol", "0")),
                ("oracle", self._oracle()),
            ]:
                test_trigger = test_trigger.replace("{%s}" % key, str(value))
        except (KeyError, TypeError):
            if isinstance(self.ground_truth, str):
                test_trigger = f'{self.ground_truth}\nprint("PASSED TESTS")'
            else:
                raise

        return test_trigger

    def exec_code(self, complete_script):
        docker_image = "ganler/evalplus"
        container_tag = f"pytester_{uuid.uuid4()}"
        start_docker_container(container_tag, docker_image)

        try:
            filepath = copy_code(complete_script, container_tag)
            status = eval_script(container_tag, "python3", filepath)
        finally:
            remove_docker_container(container_tag)

        return status

    def _run_tests(self, solution_code, trigger_code=TEST_TRIGGER):
        complete_test_script = f"""{solution_code}\n{self._construct_tests(trigger_code)}"""
        return self.exec_code(complete_test_script)

    def evaluate(self, example, response):
        solution = _validate_and_parse_evalplus_result(response)
        output = self._run_tests(solution)

        if ("PASSED TESTS" in output) and ("FAILED TESTS" not in output):
            return True, "The provided implementation passed all tests."

        if "Timeout" in output:
            return (
                False,
                "The provided implementation ran into a timeout during the testing process.",
            )

        return (False, f"The provided implementation failed. Output:\n```{output}```")


def _validate_and_parse_evalplus_result(result):
    if "```python" not in result:
        raise ValueError("Expected the result to be enclosed in ```python and ```")

    _, result = result.split("```python", 1)

    if "```" not in result:
        raise ValueError("Expected the result to be enclosed in ```python and ```")

    result, _ = result.split("```", 1)
    return result


# Test Utils ----------------------


def eval_script(container_id: str, command: str, path: str, stdin_input: str | None = None) -> str:
    """
    Implementation adapted from eval_r.py from the MultiPL-E project (https://github.com/nuprl/MultiPL-E)

    :param container_id: The container id where the script is located
    :param command: The command to run the script inside the container
    :param path: The path inside the container where the script is located
    :return: The output of the script execution
    """
    output_message = ""
    docker_cmd = (
        ["docker", "exec", "-i", container_id, command, path]
        if stdin_input is not None
        else ["docker", "exec", container_id, command, path]
    )
    encoded_input = stdin_input.encode("utf-8") if stdin_input is not None else None

    try:
        output = subprocess.run(
            docker_cmd,
            capture_output=True,
            timeout=30,
            input=encoded_input,
        )

        if output.returncode != 0:
            output_message += "Exception:\n"
        output_message += output.stdout.decode("utf-8") if output.stdout else ""
        output_message += output.stderr.decode("utf-8") if output.stderr else ""
    except subprocess.TimeoutExpired as exc:
        output_message += "Timeout during the execution of the test suite.\n"
        output_message += exc.stdout.decode("utf-8") if exc.stdout else ""
        output_message += exc.stderr.decode("utf-8") if exc.stderr else ""
    except subprocess.CalledProcessError as exc:
        output_message += "Error:\n"
        output_message += exc.stdout.decode("utf-8") if exc.stdout else ""
        output_message += exc.stderr.decode("utf-8") if exc.stderr else ""

    # Remove the file after running the script
    subprocess.run(["docker", "exec", container_id, "rm", "-f", path])

    return output_message


# Utils ----------------------------


def start_docker_container(container_id: str, container_image: str) -> None:
    """
    Start a docker container for the given image and assign the given id.

    :param container_id: The container id
    :param container_image: The container image
    """
    result = subprocess.run(
        f"docker run -m 8g --memory-swap=8g  --platform=linux/amd64 --name {container_id} --entrypoint tail -d {container_image} -f /dev/null",
        shell=True,
    )
    if result.returncode != 0:
        raise Exception(f"Error creating the container {container_image}")


def remove_docker_container(container_id: str) -> None:
    """
    Remove the docker container with the given id.

    :param container_id: The container id
    """

    result = subprocess.run(f"docker rm -f {container_id}", shell=True)
    if result.returncode != 0:
        raise Exception(f"Error removing the container {container_id}")


def copy_code(code: str, container_id: str) -> str:
    """
    Create a copy of the script in the container. Returns the path to the copied script in the container.

    :param code: The content of the source code to copy
    :param container_id: The container id where the code will be copied
    :return: The path of the copied script in the container
    """
    try:
        filename = f"temp_script_{container_id}.py"
        container_path = "/app/temp_script.py"
        with open(filename, "w") as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                f"docker cp {filename} {container_id}:{container_path}", shell=True
            )
            if result.returncode != 0:
                raise Exception("Error copying the file to the container")
    finally:
        os.remove(filename)

    return container_path


def on_script_finished():
    remove_docker_container("py-test-container")
