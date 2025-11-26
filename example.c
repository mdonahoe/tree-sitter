#include <stdio.h>
#include <string.h>
#include <tree_sitter/api.h>

// This is a simple example demonstrating tree-sitter's basic API
// Note: This requires a language grammar to parse actual code
// For a working example, you need to link against a grammar like tree-sitter-json

int main() {
    printf("Tree-sitter minimal API example\n");
    printf("================================\n\n");

    // Create a parser
    TSParser *parser = ts_parser_new();

    if (!parser) {
        fprintf(stderr, "Failed to create parser\n");
        return 1;
    }

    printf("✓ Parser created successfully\n");
    printf("  Library version: %d (min compatible: %d)\n",
           TREE_SITTER_LANGUAGE_VERSION,
           TREE_SITTER_MIN_COMPATIBLE_LANGUAGE_VERSION);

    // Note: To parse actual code, you would need to:
    // 1. Get a language grammar (e.g., tree_sitter_json())
    // 2. Set it: ts_parser_set_language(parser, tree_sitter_json());
    // 3. Parse: TSTree *tree = ts_parser_parse_string(parser, NULL, source_code, strlen(source_code));
    // 4. Work with the tree
    // 5. Clean up: ts_tree_delete(tree);

    printf("\nTo parse actual code, you need a language grammar.\n");
    printf("See tree-sitter documentation for grammar installation.\n");

    // Clean up
    ts_parser_delete(parser);
    printf("\n✓ Parser deleted successfully\n");

    return 0;
}
