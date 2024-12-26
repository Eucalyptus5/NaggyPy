import * as vscode from 'vscode';
import { execFile } from 'child_process';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
  // Create a diagnostic collection for NaggyPy
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('naggypy');
  context.subscriptions.push(diagnosticCollection);

  // Register the "naggypy.runLinter" command
  const runLinterCommand = vscode.commands.registerCommand('naggypy.runLinter', () => {
    const activeEditor = vscode.window.activeTextEditor;
    if (!activeEditor) {
      vscode.window.showWarningMessage('No active editor found to run NaggyPy Linter.');
      return;
    }

    const doc = activeEditor.document;
    if (doc.languageId !== 'python') {
      vscode.window.showInformationMessage('NaggyPy only lints Python files.');
      return;
    }

    runNaggyPyLinter(doc, diagnosticCollection);
  });

  context.subscriptions.push(runLinterCommand);

  // Optionally, run the linter automatically when a Python file is saved
  vscode.workspace.onDidSaveTextDocument((savedDoc) => {
    if (savedDoc.languageId === 'python') {
      runNaggyPyLinter(savedDoc, diagnosticCollection);
    }
  });
}

function runNaggyPyLinter(doc: vscode.TextDocument, diagColl: vscode.DiagnosticCollection) {
  const filePath = doc.fileName;

  // Adjust this path to your Python interpreter / script location
  // If your script is in the workspace root, for example:
  const pythonPath = 'python';
  const linterScriptPath = path.join(vscode.workspace.rootPath || '', 'snark_linter.py');

  // Use `--json` so we get JSON output
  execFile(pythonPath, [linterScriptPath, '--json', filePath], { cwd: vscode.workspace.rootPath }, (error, stdout, stderr) => {
    if (error) {
      vscode.window.showErrorMessage(`NaggyPy Linter failed: ${error.message}`);
      diagColl.set(doc.uri, []);
      return;
    }

    let results: Array<{ line: number, message: string }> = [];
    try {
      results = JSON.parse(stdout);
    } catch (parseErr) {
      vscode.window.showErrorMessage(`Failed to parse NaggyPy JSON output: ${parseErr}`);
      diagColl.set(doc.uri, []);
      return;
    }

    const diagnostics: vscode.Diagnostic[] = [];
    for (const issue of results) {
      const lineNum = issue.line || 1;
      const message = issue.message || 'Unknown comedic error.';
      // Lines are 0-based in VS Code
      const range = new vscode.Range(lineNum - 1, 0, lineNum - 1, 9999);

      const diag = new vscode.Diagnostic(
        range,
        message,
        vscode.DiagnosticSeverity.Warning
      );
      diagnostics.push(diag);
    }

    diagColl.set(doc.uri, diagnostics);
  });
}

export function deactivate() {
  // Cleanup if needed
}