---
name: tdd-workflow
description: 撰寫新功能、修 bug 或重構程式碼時使用此技能。強制執行測試驅動開發（TDD）流程，要求 80%+ 覆蓋率，涵蓋單元測試、整合測試與 API 測試。
---

# 測試驅動開發工作流

此技能確保所有程式碼開發遵循 TDD 原則，並具備完整的測試覆蓋。

## 啟動時機

- 撰寫新功能或新需求
- 修正 Bug 或問題
- 重構現有程式碼
- 新增 REST API 端點
- 建立新的 Service / Repository / Domain 類別

---

## 核心原則

### 1. 測試優先
**永遠先寫測試，再撰寫實作程式碼。**

### 2. 覆蓋率要求
- 最低 80%（單元測試 + 整合測試合計）
- 所有邊界條件都需測試
- 錯誤情境必須涵蓋
- 驗證邊界值（null、空值、極值）

### 3. 測試分類

#### 單元測試（Unit Test）
- 單一方法或類別邏輯
- Service 業務邏輯
- Domain / VO 計算與驗證
- 工具方法（Util / Helper）
- 使用 Mockito 隔離外部依賴

#### 整合測試（Integration Test）
- REST API 端點（使用 `@WebMvcTest` 或 `@SpringBootTest`）
- Repository 與資料庫互動（使用 `@DataJpaTest`）
- Service 層跨模組協作
- 外部 API 呼叫（使用 WireMock）

---

## TDD 開發步驟

### Step 1：撰寫使用者情境
```
身為 [角色]，我希望 [操作]，以便 [目的]

範例：
身為使用者，我希望透過關鍵字搜尋訂單，
以便快速找到歷史交易記錄。
```

### Step 2：產生測試案例
針對每個使用者情境，建立完整測試案例：

```java
@DisplayName("OrderService - 訂單搜尋")
class OrderServiceTest {

    @Test
    @DisplayName("根據關鍵字返回符合的訂單列表")
    void shouldReturnMatchingOrdersByKeyword() {
        // 測試實作
    }

    @Test
    @DisplayName("查無結果時返回空列表")
    void shouldReturnEmptyListWhenNoMatch() {
        // 測試邊界條件
    }

    @Test
    @DisplayName("關鍵字為 null 時拋出 IllegalArgumentException")
    void shouldThrowExceptionWhenKeywordIsNull() {
        // 測試錯誤情境
    }

    @Test
    @DisplayName("關鍵字超過 100 字元時拋出 ValidationException")
    void shouldThrowExceptionWhenKeywordExceedsMaxLength() {
        // 測試邊界值
    }
}
```

### Step 3：執行測試（應該失敗）
```bash
mvn test
# 測試應失敗——尚未實作
```

### Step 4：實作最小可行程式碼
撰寫最少量的程式碼讓測試通過：

```java
// 依照測試需求驅動實作
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;

    public List<OrderResponse> searchOrders(String keyword) {
        // 由測試驅動此處的實作邏輯
    }
}
```

### Step 5：再次執行測試（應該通過）
```bash
mvn test
# 測試應全部通過（綠燈）
```

### Step 6：重構
在測試保護下提升程式碼品質：
- 消除重複邏輯
- 改善命名可讀性
- 提取共用方法
- 優化效能

### Step 7：驗證覆蓋率
```bash
mvn test jacoco:report
# 查看報告：target/site/jacoco/index.html
# 確認 80%+ 覆蓋率達標
```

---

## 測試模式範例

### 單元測試模式（JUnit 5 + Mockito）

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("UserService - 使用者管理")
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    @Test
    @DisplayName("建立使用者成功，返回新建的使用者資訊")
    void shouldCreateUserSuccessfully() {
        // Arrange（準備）
        CreateUserRequest request = new CreateUserRequest("test@example.com", "password123");
        User savedUser = new User(1L, "test@example.com", "encoded_password");

        given(passwordEncoder.encode("password123")).willReturn("encoded_password");
        given(userRepository.save(any(User.class))).willReturn(savedUser);

        // Act（執行）
        UserResponse response = userService.createUser(request);

        // Assert（驗證）
        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.email()).isEqualTo("test@example.com");
        then(userRepository).should().save(any(User.class));
    }

    @Test
    @DisplayName("Email 已存在時拋出 DuplicateEmailException")
    void shouldThrowExceptionWhenEmailAlreadyExists() {
        // Arrange
        CreateUserRequest request = new CreateUserRequest("existing@example.com", "password123");
        given(userRepository.existsByEmail("existing@example.com")).willReturn(true);

        // Act & Assert
        assertThatThrownBy(() -> userService.createUser(request))
            .isInstanceOf(DuplicateEmailException.class)
            .hasMessage("Email 已被使用：existing@example.com");
    }

    @Test
    @DisplayName("使用者不存在時拋出 UserNotFoundException")
    void shouldThrowExceptionWhenUserNotFound() {
        // Arrange
        given(userRepository.findById(999L)).willReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> userService.findById(999L))
            .isInstanceOf(UserNotFoundException.class);
    }
}
```

### API 整合測試模式（@WebMvcTest）

```java
@WebMvcTest(UserController.class)
@DisplayName("GET/POST /api/v1/users")
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("GET /api/v1/users/{id} - 查詢成功返回 200")
    void shouldReturnUserWhenExists() throws Exception {
        // Arrange
        UserResponse user = new UserResponse(1L, "test@example.com");
        given(userService.findById(1L)).willReturn(user);

        // Act & Assert
        mockMvc.perform(get("/api/v1/users/1")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.id").value(1))
            .andExpect(jsonPath("$.data.email").value("test@example.com"));
    }

    @Test
    @DisplayName("POST /api/v1/users - 建立成功返回 201")
    void shouldCreateUserAndReturn201() throws Exception {
        // Arrange
        CreateUserRequest request = new CreateUserRequest("new@example.com", "password123");
        UserResponse created = new UserResponse(2L, "new@example.com");
        given(userService.createUser(any())).willReturn(created);

        // Act & Assert
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"))
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.id").value(2));
    }

    @Test
    @DisplayName("POST /api/v1/users - 參數驗證失敗返回 400")
    void shouldReturn400WhenValidationFails() throws Exception {
        // Arrange - email 格式錯誤
        CreateUserRequest invalidRequest = new CreateUserRequest("not-an-email", "pwd");

        // Act & Assert
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidRequest)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.success").value(false))
            .andExpect(jsonPath("$.error.code").value("VALIDATION_FAILED"));
    }

    @Test
    @DisplayName("GET /api/v1/users/{id} - 使用者不存在返回 404")
    void shouldReturn404WhenUserNotFound() throws Exception {
        // Arrange
        given(userService.findById(999L)).willThrow(new UserNotFoundException("使用者不存在"));

        // Act & Assert
        mockMvc.perform(get("/api/v1/users/999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.success").value(false))
            .andExpect(jsonPath("$.error.code").value("USER_NOT_FOUND"));
    }
}
```

### Repository 整合測試模式（@DataJpaTest）

```java
@DataJpaTest
@DisplayName("OrderRepository - 資料存取")
class OrderRepositoryTest {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private TestEntityManager entityManager;

    @Test
    @DisplayName("依狀態查詢訂單，只返回符合狀態的記錄")
    void shouldFindOrdersByStatus() {
        // Arrange
        Order pendingOrder = new Order("ORD-001", OrderStatus.PENDING);
        Order completedOrder = new Order("ORD-002", OrderStatus.COMPLETED);
        entityManager.persist(pendingOrder);
        entityManager.persist(completedOrder);
        entityManager.flush();

        // Act
        List<Order> result = orderRepository.findByStatus(OrderStatus.PENDING);

        // Assert
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getOrderNumber()).isEqualTo("ORD-001");
    }

    @Test
    @DisplayName("查詢不存在的訂單編號返回 Optional.empty()")
    void shouldReturnEmptyWhenOrderNumberNotFound() {
        // Act
        Optional<Order> result = orderRepository.findByOrderNumber("NON-EXISTENT");

        // Assert
        assertThat(result).isEmpty();
    }
}
```

---

## 測試檔案組織結構

```
src/
├── main/java/com/example/
│   ├── controller/
│   │   └── UserController.java
│   ├── service/
│   │   └── UserService.java
│   ├── repository/
│   │   └── UserRepository.java
│   └── domain/
│       └── User.java
└── test/java/com/example/
    ├── controller/
    │   └── UserControllerTest.java      # API 整合測試（@WebMvcTest）
    ├── service/
    │   └── UserServiceTest.java          # 單元測試（@ExtendWith + @Mock）
    ├── repository/
    │   └── UserRepositoryTest.java       # Repository 整合測試（@DataJpaTest）
    └── integration/
        └── UserFlowIntegrationTest.java  # 完整流程整合測試（@SpringBootTest）
```

---

## Mock 外部依賴

### Mock 第三方 API（WireMock）
```java
@SpringBootTest
@WireMockTest  // 類別層級 annotation，自動啟動 WireMock server
class PaymentServiceTest {

    @Autowired
    private PaymentService paymentService;

    @Test
    @DisplayName("付款閘道回應成功時，返回成功的交易結果")
    void shouldCallPaymentGatewaySuccessfully(WireMockRuntimeInfo wmInfo) {
        // Arrange
        stubFor(post(urlEqualTo("/payment/charge"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("{\"transactionId\": \"TXN-123\", \"status\": \"SUCCESS\"}")));

        // Act
        PaymentResult result = paymentService.charge(new ChargeRequest(1000L, "TWD"));

        // Assert
        assertThat(result.status()).isEqualTo("SUCCESS");
        assertThat(result.transactionId()).isEqualTo("TXN-123");
    }
}
```

### Mock Spring Bean
```java
@SpringBootTest
class OrderServiceIntegrationTest {

    @MockBean
    private EmailNotificationService emailService; // 替換真實 Bean

    @Autowired
    private OrderService orderService;

    @Test
    @DisplayName("訂單成立後，通知服務應被呼叫一次")
    void shouldSendNotificationAfterOrderCreated() {
        // Act
        orderService.createOrder(new CreateOrderRequest(...));

        // Assert
        verify(emailService, times(1)).sendOrderConfirmation(any());
    }
}
```

---

## JaCoCo 覆蓋率設定

### pom.xml 設定
```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                            <limit>
                                <counter>BRANCH</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### 執行覆蓋率報告
```bash
# 執行測試並產生覆蓋率報告
mvn test jacoco:report

# 報告位置
open target/site/jacoco/index.html

# 若覆蓋率未達標，build 會失敗
mvn verify
```

---

## 常見測試錯誤

### ❌ 錯誤：測試實作細節
```java
// 不要驗證內部狀態或 private 方法
assertThat(orderService.getInternalCache()).hasSize(5);
```

### ✅ 正確：測試行為與結果
```java
// 驗證使用者可見的行為
List<OrderResponse> orders = orderService.searchOrders("test");
assertThat(orders).hasSize(5);
```

### ❌ 錯誤：測試間互相依賴
```java
// 測試 A 建立資料，測試 B 依賴 A 留下的資料
@Test void createOrder() { /* 建立訂單 */ }
@Test void findOrder()   { /* 假設訂單已存在 */ }
```

### ✅ 正確：每個測試自給自足
```java
@BeforeEach
void setUp() {
    // 每個測試前重置狀態
    orderRepository.deleteAll();
}

@Test
void shouldFindCreatedOrder() {
    Order order = orderRepository.save(new Order(...)); // 自行準備資料
    Optional<Order> found = orderRepository.findById(order.getId());
    assertThat(found).isPresent();
}
```

### ❌ 錯誤：Mock 過多，測試沒有意義
```java
// 所有東西都 mock，實際上沒有測試任何邏輯
given(orderService.calculate(any())).willReturn(100L);
assertThat(orderService.calculate(order)).isEqualTo(100L); // 廢話
```

### ✅ 正確：只 Mock 外部依賴
```java
// 只 mock 真正的外部依賴（DB、外部 API）
given(paymentGateway.charge(any())).willReturn(new ChargeResult("SUCCESS"));
// 測試 service 本身的業務邏輯
PaymentResult result = paymentService.processPayment(order);
assertThat(result.isSuccess()).isTrue();
```

---

## 測試最佳實踐

1. **測試優先** — 永遠先寫測試，再實作程式碼（Red → Green → Refactor）
2. **一個測試一個行為** — 每個 `@Test` 只驗證單一行為，失敗訊息才有意義
3. **描述性測試名稱** — 用 `@DisplayName` 清楚說明測試的情境與預期結果
4. **Arrange-Act-Assert 結構** — 三段式：準備資料 → 執行動作 → 驗證結果
5. **只 Mock 外部依賴** — Repository、外部 API、Email Service 才 Mock；業務邏輯不 Mock
6. **測試邊界條件** — null、空字串、空列表、極大值、極小值都要涵蓋
7. **測試錯誤路徑** — 不只測成功情境，Exception 情境同樣重要
8. **保持測試快速** — 單元測試每個 < 50ms；`@DataJpaTest` 和 `@WebMvcTest` 用 Slice Test 代替 `@SpringBootTest`
9. **測試後清理狀態** — 使用 `@Transactional` 或 `@BeforeEach` / `@AfterEach` 確保測試隔離，無副作用
10. **定期檢視覆蓋率報告** — `mvn test jacoco:report`，找出未覆蓋的分支並補測試

---

## 持續測試

### 開發中持續執行
```bash
# 監聽檔案變化，自動重新執行測試（需搭配 Maven Wrapper 或 IDE）
mvn test -Dtest=UserServiceTest  # 只跑特定測試類別

# 執行特定方法
mvn test -Dtest="UserServiceTest#shouldCreateUserSuccessfully"
```

### 完整驗證
```bash
mvn clean verify    # 編譯 + 測試 + 覆蓋率驗證
```

---

## 成功指標

- 80%+ 程式碼覆蓋率（Line + Branch）
- 所有測試通過（綠燈）
- 無 `@Disabled` 或跳過的測試
- 單元測試執行時間 < 50ms / 個
- `mvn clean verify` 全程通過
- 測試涵蓋正常路徑、錯誤路徑、邊界條件

---

**記住**：測試不是可選項，是讓你能安心重構、快速交付、確保生產穩定的安全網。沒有測試保護的程式碼，是技術債的溫床。
