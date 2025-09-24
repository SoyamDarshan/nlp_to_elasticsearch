package com.example.nlpapi.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class NlpController {
    private static final Logger logger = LoggerFactory.getLogger(NlpController.class);

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    @PostMapping("/nlp-query")
    public ResponseEntity<?> handlePrompt(@RequestBody Map<String, String> body) {
        String prompt = body.get("prompt");
        logger.info("[Java API] Received prompt: {}", prompt);
        RestTemplate restTemplate = new RestTemplate();
        logger.info("[Java API] Sending request to Python service at: {}", pythonServiceUrl + "/process");
        ResponseEntity<Map> response = restTemplate.postForEntity(
            pythonServiceUrl + "/process", body, Map.class);
        logger.info("[Java API] Received response from Python service: {}", response.getBody());

        Map<String, Object> pyResp = response.getBody();
        Object intent = pyResp.get("intent");
        Object resultObj = pyResp.get("results");
        // Unwrap {data: {_source: ...}} or {data: ...} or {_source: ...} if needed
        Object result = resultObj;
        if (resultObj instanceof Map) {
            Map itemMap = (Map) resultObj;
            Object data = itemMap.get("data");
            if (data instanceof Map && ((Map) data).containsKey("_source")) {
                result = ((Map) data).get("_source");
            } else if (data instanceof Map) {
                result = data;
            } else if (itemMap.containsKey("_source")) {
                result = itemMap.get("_source");
            }
        }
        Map<String, Object> frontendResp = new java.util.HashMap<>();
        frontendResp.put("intent", intent);
        frontendResp.put("results", result);
        ResponseEntity<?> frontendResponse = ResponseEntity.ok(frontendResp);
        logger.info("[Java API] Outgoing HTTP status: {}", frontendResponse.getStatusCode());
        logger.info("[Java API] Outgoing response body: {}", frontendResp);
        return frontendResponse;
    }

    @PostMapping("/repopulate-es")
    public ResponseEntity<?> repopulateEs() {
        logger.info("[Java API] Received request to repopulate ES index");
        RestTemplate restTemplate = new RestTemplate();
        logger.info("[Java API] Sending repopulate request to Python service at: {}", pythonServiceUrl + "/repopulate-es");
        ResponseEntity<Map> response = restTemplate.postForEntity(
            pythonServiceUrl + "/repopulate-es", null, Map.class);
        logger.info("[Java API] Received response from Python service: {}", response.getBody());
        return ResponseEntity.ok(response.getBody());
    }
}
