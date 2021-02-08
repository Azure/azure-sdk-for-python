Import-Module Pester

BeforeAll {
    . ./job-matrix-functions.ps1
}

Describe "Platform Matrix nonSparse" -Tag "nonsparse" {
    BeforeEach {
        $matrixJson = @'
{
    "matrix": {
        "testField1": [ 1, 2 ],
        "testField2": [ 1, 2, 3 ],
        "testField3": [ 1, 2, 3, 4 ],
    }
}
'@
        $config = GetMatrixConfigFromJson $matrixJson
    }

    It "Should process nonSparse parameters" {
        $parameters, $nonSparse = ProcessNonSparseParameters $config.orderedMatrix "testField1","testField3"
        $parameters.Count | Should -Be 1
        $parameters["testField2"] | Should -Be 1,2,3
        $nonSparse.Count | Should -Be 2
        $nonSparse["testField1"] | Should -Be 1,2
        $nonSparse["testField3"] | Should -Be 1,2,3,4

        $parameters, $nonSparse = ProcessNonSparseParameters $config.orderedMatrix "testField3"
        $parameters.Count | Should -Be 2
        $parameters.Contains("testField3") | Should -Be $false
        $nonSparse.Count | Should -Be 1
        $nonSparse["testField3"] | Should -Be 1,2,3,4
    }

    It "Should ignore nonSparse with all selection" {
        $matrix = GenerateMatrix $config "all" -nonSparseParameters "testField3"
        $matrix.Length | Should -Be 24
    }

    It "Should combine sparse matrix with nonSparse parameters" {
        $matrix = GenerateMatrix $config "sparse" -nonSparseParameters "testField3"
        $matrix.Length | Should -Be 12
    }

    It "Should combine with multiple nonSparse fields" {
        $matrixJson = @'
{
    "matrix": {
        "testField1": [ 1, 2 ],
        "testField2": [ 1, 2 ],
        "testField3": [ 31, 32 ],
        "testField4": [ 41, 42 ]
    }
}
'@
        $config = GetMatrixConfigFromJson $matrixJson

        $matrix = GenerateMatrix $config "all" -nonSparseParameters "testField3","testField4"
        $matrix.Length | Should -Be 16

        $matrix = GenerateMatrix $config "sparse" -nonSparseParameters "testField3","testField4"
        $matrix.Length | Should -Be 8
    }
}

Describe "Platform Matrix Import" -Tag "import" {
    It "Should generate a matrix with nonSparseParameters and an imported sparse matrix" {
        $matrixJson = @'
{
    "matrix": {
        "$IMPORT": "./test-import-matrix.json",
        "testField": [ "test1", "test2" ]
    }
}
'@
        $importConfig = GetMatrixConfigFromJson $matrixJson
        $matrix = GenerateMatrix $importConfig "sparse" -nonSparseParameters "testField"

        $matrix.Length | Should -Be 6

        $matrix[0].name | Should -Be test1_foo1_bar1
        $matrix[0].parameters.testField | Should -Be "test1"
        $matrix[0].parameters.Foo | Should -Be "foo1"
        $matrix[2].name | Should -Be test1_importedBaz
        $matrix[2].parameters.testField | Should -Be "test1"
        $matrix[2].parameters.Baz | Should -Be "importedBaz"
        $matrix[4].name | Should -Be test2_foo2_bar2
        $matrix[4].parameters.testField | Should -Be "test2"
        $matrix[4].parameters.Foo | Should -Be "foo2"
    }

    It "Should generate a sparse matrix with an imported a sparse matrix" {
        $matrixJson = @'
{
    "matrix": {
        "$IMPORT": "./test-import-matrix.json",
        "testField1": [ "test11", "test12" ],
        "testField2": [ "test21", "test22" ]
    }
}
'@
        $importConfig = GetMatrixConfigFromJson $matrixJson
        $matrix = GenerateMatrix $importConfig "sparse"

        $matrix.Length | Should -Be 6

        $matrix[0].name | Should -Be test11_test21_foo1_bar1
        $matrix[0].parameters.testField1 | Should -Be "test11"
        $matrix[0].parameters.testField2 | Should -Be "test21"
        $matrix[0].parameters.Foo | Should -Be "foo1"
        $matrix[2].name | Should -Be test11_test21_importedBaz
        $matrix[2].parameters.testField1 | Should -Be "test11"
        $matrix[2].parameters.testField2 | Should -Be "test21"
        $matrix[2].parameters.Baz | Should -Be "importedBaz"
        $matrix[4].name | Should -Be test12_test22_foo2_bar2
        $matrix[4].parameters.testField1 | Should -Be "test12"
        $matrix[4].parameters.testField2 | Should -Be "test22"
        $matrix[4].parameters.Foo | Should -Be "foo2"
    }

    It "Should generate different matrices when importing and not importing" {
        $importMatrixJson = @'
{
    "matrix": {
        "$IMPORT": "./test-import-matrix.json",
        "testField1": [ "test11", "test12" ]
    }
}
'@
        $matrixJson = @'
{
    "matrix": {
        "testField1": [ "test11", "test12" ]
    }
}
'@
        $configToImport = GetMatrixConfigFromJson (Get-Content test-import-matrix.json)
        $matrixToImport = GenerateMatrix $configToImport "sparse"
        $importConfig = GetMatrixConfigFromJson $importMatrixJson
        $matrixWithImport = GenerateMatrix $importConfig "sparse"
        $nonImportConfig = GetMatrixConfigFromJson $matrixJson
        $matrixWithoutImport = GenerateMatrix $nonImportConfig "sparse"

        $matrixToImport.Length | Should -Be 3
        $matrixWithoutImport.Length | Should -Be 2
        $matrixWithImport.Length | Should -Be 6

        $combined = CombineMatrices $matrixWithoutImport $matrixToImport
        $combined.Length | Should -Be 6

        for ($i = 0; $i -lt $matrixWithImport.Length; $i++) {
            foreach ($entry in $matrixWithImport[$i]) {
                $combined[$i].name | Should -Be $entry.name
                foreach ($param in $entry.parameters.GetEnumerator()) {
                    $combined[$i].parameters[$param.Name] | Should -Be $param.Value
                }
            }
        }
    }

    It "Should import a sparse matrix with import, include, and exclude" {
        $matrixJson = @'
{
    "matrix": {
        "$IMPORT": "./test-import-matrix.json",
        "testField": [ "test1", "test2", "test3" ],
    },
    "include": [
      {
        "testImportIncludeName": [ "testInclude1", "testInclude2" ]
      }
    ],
    "exclude": [
      {
        "testField": "test1"
      },
      {
        "testField": "test3",
        "Baz": "importedBaz"
      }
    ]
}
'@

        $importConfig = GetMatrixConfigFromJson $matrixJson
        $matrix = GenerateMatrix $importConfig "sparse"

        $matrix.Length | Should -Be 7
    }
}
