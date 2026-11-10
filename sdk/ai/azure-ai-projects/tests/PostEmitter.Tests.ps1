# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

Describe 'PostEmitter union alias references' {
    BeforeAll {
        $postEmitter = Join-Path $PSScriptRoot '..\PostEmitter.ps1'
        $tokens = $null
        $parseErrors = $null
        $ast = [System.Management.Automation.Language.Parser]::ParseFile(
            $postEmitter, [ref]$tokens, [ref]$parseErrors
        )
        if ($parseErrors.Count) {
            throw ($parseErrors.Message -join "`n")
        }
        $repairFunction = $ast.Find({
            param($node)
            $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
                $node.Name -eq 'Repair-UnionAliasReferences'
        }, $true)
        if ($null -eq $repairFunction) {
            throw 'Repair-UnionAliasReferences was not found in PostEmitter.ps1.'
        }
        . ([scriptblock]::Create($repairFunction.Extent.Text))
    }

    It 'repairs scalar and list references while preserving model references' {
        $content = @'
EvalItemContentItem: TypeAlias = Union[str, "_models.EvalItemContentItemObject"]
EvalItemContent: TypeAlias = Union["_unions.EvalItemContentItem", list["_unions.EvalItemContentItem"]]
'@
        $expected = @'
EvalItemContentItem: TypeAlias = Union[str, "_models.EvalItemContentItemObject"]
EvalItemContent: TypeAlias = Union["EvalItemContentItem", list["EvalItemContentItem"]]
'@
        Repair-UnionAliasReferences -Content $content | Should BeExactly $expected
    }

    It 'repairs single-quoted references and leaves other namespaces unchanged' {
        $content = "Alias = Union['_unions.Item', '_models.Model', 'other_unions.Item']"
        $expected = "Alias = Union['Item', '_models.Model', 'other_unions.Item']"
        Repair-UnionAliasReferences -Content $content | Should BeExactly $expected
    }

    It 'preserves line endings and trailing newlines' -TestCases @(
        @{ NewLine = "`n" }, @{ NewLine = "`r`n" }
    ) {
        param($NewLine)
        $content = 'First = "_unions.Item"' + $NewLine + 'Second = "_models.Model"' + $NewLine
        $expected = 'First = "Item"' + $NewLine + 'Second = "_models.Model"' + $NewLine
        Repair-UnionAliasReferences -Content $content | Should BeExactly $expected
    }

    It 'leaves already-correct content unchanged on repeated runs' {
        $content = 'Alias: TypeAlias = Union["Item", list["Item"], "_models.Model"]'
        $once = Repair-UnionAliasReferences -Content $content
        $twice = Repair-UnionAliasReferences -Content $once
        $once | Should BeExactly $content
        $twice | Should BeExactly $content
    }
}
