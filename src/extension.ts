import * as vscode from 'vscode';
import { execFile } from 'child_process';

export function activate(context: vscode.ExtensionContext) {

  // Create a diagnostic collection for NaggyPy
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('naggypy');
  context.subscriptions.push(diagnosticCollection);

  // Register the "naggypy.runLinter" command
  const runLinterCommand = vscode.commands.registerCommand('naggypy.runLinter', () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('No active editor for NaggyPy Linter.');
      return;
    }

    if (editor.document.languageId !== 'python') {
      vscode.window.showInformationMessage('NaggyPy only lints Python files.');
      return;
    }

    // Actually run the linter
    runNaggyPyLinter(editor.document, context, diagnosticCollection);
  });

  context.subscriptions.push(runLinterCommand);

  // Optionally lint on save
  vscode.workspace.onDidSaveTextDocument((doc) => {
    if (doc.languageId === 'python') {
      runNaggyPyLinter(doc, context, diagnosticCollection);
    }
  });
}

function runNaggyPyLinter(
  doc: vscode.TextDocument,
  context: vscode.ExtensionContext,
  diagColl: vscode.DiagnosticCollection
) {
  const filePath = doc.fileName;

  // path to python interpreter (assuming 'python' is on PATH)
  const pythonPath = 'python';

  const linterScript = context.asAbsolutePath('snark_linter.py');

  // Spawn the process: python <snark_linter.py> --json <filePath>
  execFile(
    pythonPath,
    [linterScript, '--json', filePath],
    (error, stdout, stderr) => {
      if (error) {
        vscode.window.showErrorMessage(`NaggyPy Linter failed: ${error.message}`);
        diagColl.set(doc.uri, []);
        return;
      }

      // Attempt to parse JSON output
      let issues: Array<{ line: number, message: string }> = [];
      try {
        issues = JSON.parse(stdout);
      } catch (e) {
        vscode.window.showErrorMessage(`Failed to parse NaggyPy JSON output: ${e}`);
        diagColl.set(doc.uri, []);
        return;
      }

      // Convert each comedic issue to a VS Code Diagnostic
      const diagnostics: vscode.Diagnostic[] = [];
      for (const issue of issues) {
        const line = issue.line || 1;
        const msg = issue.message || 'Unknown comedic error.';
        // lines are zero-based in VS Code
        const range = new vscode.Range(line - 1, 0, line - 1, 9999);
        const diagnostic = new vscode.Diagnostic(
          range,
          msg,
          vscode.DiagnosticSeverity.Warning
        );
        diagnostics.push(diagnostic);
      }

      diagColl.set(doc.uri, diagnostics);
    }
  );
}

export function deactivate() {
  // cleanup if needed
}