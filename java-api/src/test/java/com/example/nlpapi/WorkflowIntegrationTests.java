package com.example.nlpapi;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.ResponseEntity;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class WorkflowIntegrationTests {

    @Autowired
    private TestRestTemplate restTemplate;

    @LocalServerPort
    private int port;

    @Test
    void testFullWorkflow_showAll() {
        System.out.println("[TEST] testFullWorkflow_showAll: starting");
        java.util.Map<String, String> body = new java.util.HashMap<>();
        body.put("prompt", "show all");
        String url = "http://localhost:" + port + "/api/nlp-query";
        System.out.println("[TEST] testFullWorkflow_showAll: POST " + url);
        ResponseEntity<String> response = restTemplate.postForEntity(url, body, String.class);
        System.out.println("[TEST] testFullWorkflow_showAll: Status: " + response.getStatusCode());
        System.out.println("[TEST] testFullWorkflow_showAll: Body: " + response.getBody());
        // TEMP: Always fail to print status and body
        org.junit.jupiter.api.Assertions.fail("TEMP DEBUG: Status: " + response.getStatusCode() + ", Body: " + response.getBody());
        assertThat(response.getStatusCode().is2xxSuccessful())
            .withFailMessage("Expected 2xx but got %s. Body: %s", response.getStatusCode(), response.getBody())
            .isTrue();
        assertThat(response.getBody())
            .withFailMessage("Body did not contain 'results'. Actual body: %s", response.getBody())
            .contains("results");
    }

    @Test
    void testFullWorkflow_log4jscanner() {
        System.out.println("[TEST] testFullWorkflow_log4jscanner: starting");
        java.util.Map<String, String> body = new java.util.HashMap<>();
        body.put("prompt", "show me log4jscanner");
        String url = "http://localhost:" + port + "/api/nlp-query";
        System.out.println("[TEST] testFullWorkflow_log4jscanner: POST " + url);
        ResponseEntity<String> response = restTemplate.postForEntity(url, body, String.class);
        System.out.println("[TEST] testFullWorkflow_log4jscanner: Status: " + response.getStatusCode());
        System.out.println("[TEST] testFullWorkflow_log4jscanner: Body: " + response.getBody());
        // TEMP: Always fail to print status and body
        org.junit.jupiter.api.Assertions.fail("TEMP DEBUG: Status: " + response.getStatusCode() + ", Body: " + response.getBody());
        assertThat(response.getStatusCode().is2xxSuccessful())
            .withFailMessage("Expected 2xx but got %s. Body: %s", response.getStatusCode(), response.getBody())
            .isTrue();
        assertThat(response.getBody())
            .withFailMessage("Body did not contain 'log4jscanner'. Actual body: %s", response.getBody())
            .contains("log4jscanner");
    }

    @Test
    void testFullWorkflow_cve() {
        System.out.println("[TEST] testFullWorkflow_cve: starting");
        java.util.Map<String, String> body = new java.util.HashMap<>();
        body.put("prompt", "show me CVE-2021-44228");
        String url = "http://localhost:" + port + "/api/nlp-query";
        System.out.println("[TEST] testFullWorkflow_cve: POST " + url);
        ResponseEntity<String> response = restTemplate.postForEntity(url, body, String.class);
        System.out.println("[TEST] testFullWorkflow_cve: Status: " + response.getStatusCode());
        System.out.println("[TEST] testFullWorkflow_cve: Body: " + response.getBody());
        // TEMP: Always fail to print status and body
        org.junit.jupiter.api.Assertions.fail("TEMP DEBUG: Status: " + response.getStatusCode() + ", Body: " + response.getBody());
        assertThat(response.getStatusCode().is2xxSuccessful())
            .withFailMessage("Expected 2xx but got %s. Body: %s", response.getStatusCode(), response.getBody())
            .isTrue();
        assertThat(response.getBody())
            .withFailMessage("Body did not contain 'CVE-2021-44228'. Actual body: %s", response.getBody())
            .contains("CVE-2021-44228");
    }
}
