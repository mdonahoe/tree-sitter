#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tree_sitter/api.h>

// Declare the C language parser
TSLanguage *tree_sitter_c(void);

// Read file contents into a string
char* read_file(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        return NULL;
    }

    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);

    char* content = malloc(length + 1);
    if (!content) {
        fclose(file);
        return NULL;
    }

    fread(content, 1, length, file);
    content[length] = '\0';
    fclose(file);

    return content;
}

// Extract text from source code given a node
void print_node_text(const char* source, TSNode node) {
    uint32_t start = ts_node_start_byte(node);
    uint32_t end = ts_node_end_byte(node);

    for (uint32_t i = start; i < end; i++) {
        putchar(source[i]);
    }
    putchar('\n');
}

int main(int argc, char** argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <filename> <query>\n", argv[0]);
        fprintf(stderr, "Example: %s example.c \"(string_literal)\"\n", argv[0]);
        return 1;
    }

    const char* filename = argv[1];
    const char* query_string = argv[2];

    // Read source file
    char* source_code = read_file(filename);
    if (!source_code) {
        return 1;
    }

    // Create parser
    TSParser* parser = ts_parser_new();
    if (!parser) {
        fprintf(stderr, "Error: Failed to create parser\n");
        free(source_code);
        return 1;
    }

    // Set language to C
    if (!ts_parser_set_language(parser, tree_sitter_c())) {
        fprintf(stderr, "Error: Failed to set language\n");
        ts_parser_delete(parser);
        free(source_code);
        return 1;
    }

    // Parse the source code
    TSTree* tree = ts_parser_parse_string(parser, NULL, source_code, strlen(source_code));
    if (!tree) {
        fprintf(stderr, "Error: Failed to parse source code\n");
        ts_parser_delete(parser);
        free(source_code);
        return 1;
    }

    // Create query
    uint32_t error_offset;
    TSQueryError error_type;
    TSQuery* query = ts_query_new(
        tree_sitter_c(),
        query_string,
        strlen(query_string),
        &error_offset,
        &error_type
    );

    if (!query) {
        fprintf(stderr, "Error: Failed to create query\n");
        fprintf(stderr, "Query error at offset %u: ", error_offset);
        switch (error_type) {
            case TSQueryErrorSyntax:
                fprintf(stderr, "Syntax error\n");
                break;
            case TSQueryErrorNodeType:
                fprintf(stderr, "Invalid node type\n");
                break;
            case TSQueryErrorField:
                fprintf(stderr, "Invalid field\n");
                break;
            case TSQueryErrorCapture:
                fprintf(stderr, "Invalid capture\n");
                break;
            default:
                fprintf(stderr, "Unknown error\n");
                break;
        }
        ts_tree_delete(tree);
        ts_parser_delete(parser);
        free(source_code);
        return 1;
    }

    // Execute query
    TSQueryCursor* cursor = ts_query_cursor_new();
    TSNode root_node = ts_tree_root_node(tree);
    ts_query_cursor_exec(cursor, query, root_node);

    // Iterate through matches
    TSQueryMatch match;
    int match_count = 0;

    while (ts_query_cursor_next_match(cursor, &match)) {
        for (uint16_t i = 0; i < match.capture_count; i++) {
            TSQueryCapture capture = match.captures[i];
            print_node_text(source_code, capture.node);
            match_count++;
        }
    }

    if (match_count == 0) {
        fprintf(stderr, "No matches found\n");
    }

    // Cleanup
    ts_query_cursor_delete(cursor);
    ts_query_delete(query);
    ts_tree_delete(tree);
    ts_parser_delete(parser);
    free(source_code);

    return 0;
}
