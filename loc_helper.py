from pathlib import Path
import json
import sys

import rich
import rich.prompt
import rich.console
import rich.highlighter

WORK_FILE = Path("output") / "localisation_work_file.json"


def load_work_file():
    with open(WORK_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_work_file(data, file_name=None):
    if file_name is None:
        file_name = WORK_FILE
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def replace_value(work_file, old_value, new_value, auto_approve=False):
    class Highlighter(rich.highlighter.Highlighter):
        def highlight(self, text):
            text = text.replace(old_value, f"[yellow]{old_value}[/yellow]")
            text = text.replace(new_value, f"[yellow]{new_value}[/yellow]")
            return text

    console = rich.console.Console()
    prompt = rich.prompt.Prompt(console=console)
    highlighter = Highlighter()

    to_be_changed = []
    for key, value in work_file.items():
        if old_value in value["loc_new"]:
            to_be_changed.append((key, value))

    if not to_be_changed:
        console.print("[green]No changes to be made[/green]")
        return

    comparisons = []
    for i, (key, value) in enumerate(to_be_changed):
        console.print(f"[{i+1}/{len(to_be_changed)}]")
        loc_new = value["loc_new"].replace(old_value, new_value)

        comparison_text = f"{'-'*10}\n[bold]Before:[/bold]\n[red]{highlighter.highlight(value['loc_new']
            )}[/red] \n[bold]After:[/bold]\n[green]{highlighter.highlight(loc_new)}[/green]\n\n"
        comparisons.append(comparison_text)

        if auto_approve:
            work_file[key]["loc_new"] = loc_new
            continue

        console.print(comparison_text)
        approved = prompt.ask("[bold]Approve?[/bold] (y/n/all): ")
        if approved == "y":
            work_file[key]["loc_new"] = loc_new
        elif approved == "all":
            auto_approve = True
            work_file[key]["loc_new"] = loc_new
            continue
        else:
            console.print("[red]Rejected[/red]")

    if prompt.ask("[bold]Show overview?[/bold] (y/n): ") == "y":
        for comparison in comparisons:
            console.print(comparison)
    if prompt.ask("[bold]Continue to save?[/bold] (y/n): ") == "y":
        save_work_file(work_file)
    else:
        console.print("[red]Aborted[/red]")
        return

    save_work_file(work_file)


def main(args: list[str]):
    if len(args) == 0:
        raise ValueError("Usage: python loc_helper.py -r <old_value> <new_value> [-y]")
    if args[0] == "-r":
        if len(args) != 3:
            raise ValueError("Usage: python loc_helper.py -r <old_value> <new_value> [-y]")
        old_value = args[1]
        new_value = args[2]
        auto_approve = len(args) > 3 and args[3] == "-y"
        print(f"Replacing {old_value} with {new_value}")
        work_file = load_work_file()
        replace_value(work_file, old_value, new_value, auto_approve)
    else:
        raise ValueError("Usage: python loc_helper.py -r <old_value> <new_value> [-y]")


if __name__ == "__main__":
    main(sys.argv[1:])
