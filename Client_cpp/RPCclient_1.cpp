#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <chrono>
#include <thread>
#include <mutex>
#include <cpprest/http_client.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// HTTP client
class HTTPClient {
public:
    HTTPClient(const std::string& url) : m_url(url), m_headers({ {"User-Agent", "Mozilla/5.0"} }) {}
    pplx::task<http_response> call(const std::string& param) {
        json Params = { {"id", param} };
        return client.post(m_url, Params.dump(), "application/json").then([](http_response response) {
            return response;
        });
    }
private:
    http_client client{ m_url };
    const std::string m_url;
    const http_headers m_headers;
};

// RPC client
class RPCClient {
public:
    RPCClient(const std::string& url) : m_url(url), m_headers({ {"Content-type", "application/json"} }) {}
    json call(const std::string& rpcMethod, const json& rpcParams) {
        int id = std::rand() % (int)(std::pow(10, 13) - std::pow(10, 12)) + std::pow(10, 12);
        json payload = {
            {"method", rpcMethod},
            {"params", rpcParams},
            {"jsonrpc", "2.0"},
            {"id", id}
        };
        return client.request(methods::POST, m_url, payload.dump(), "application/json").then([](http_response response) {
            return response.extract_json();
        }).then([](json response) {
            return response["result"];
        }).get();
    }
private:
    http_client client{ m_url };
    const std::string m_url;
    const http_headers m_headers;
};
