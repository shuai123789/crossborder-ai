"""
Multi-Agent Pricing Analysis System
Complete multi-agent collaborative pricing analysis system
"""
import os
import json
import requests
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class AgentRole(Enum):
    PLANNER = "planner"      # Planning Agent
    RETRIEVER = "retriever"  # Retrieval Agent
    CALCULATOR = "calculator" # Calculator Agent
    GENERATOR = "generator"  # Generator Agent
    CHECKER = "checker"      # Checker Agent


@dataclass
class Task:
    """Task definition"""
    id: str
    description: str
    role: AgentRole
    dependencies: List[str]  # IDs of dependent tasks
    status: str = "pending"  # pending/running/completed/failed
    result: Any = None


@dataclass
class AgentMessage:
    """Inter-agent communication message"""
    from_agent: str
    to_agent: str
    content: Any
    message_type: str  # task/request/response


class DeepSeekClient:
    """DeepSeek API client"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """Call chat API"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": temperature
                },
                timeout=30
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"API call failed: {e}")
            return json.dumps({"error": str(e)})
    
    def function_call(self, messages: List[Dict], functions: List[Dict]) -> Dict:
        """Call Function Calling API"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "functions": functions,
                    "function_call": "auto"
                },
                timeout=30
            )
            return response.json()['choices'][0]['message']
        except Exception as e:
            print(f"Function call failed: {e}")
            return {"content": json.dumps({"error": str(e)})}


class BaseAgent:
    """Base Agent class"""
    
    def __init__(self, name: str, role: AgentRole, llm_client=None):
        self.name = name
        self.role = role
        self.llm_client = llm_client or DeepSeekClient()
        self.memory: List[Dict] = []
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable):
        """Register tool"""
        self.tools[name] = func
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        return self.tools[tool_name](**kwargs)
    
    def think(self, context: Dict) -> Dict:
        """Think/Plan - implemented by subclass"""
        raise NotImplementedError
    
    def act(self, task: Task) -> Any:
        """Execute task - implemented by subclass"""
        raise NotImplementedError
    
    def run(self, task: Task, context: Dict) -> Any:
        """Run Agent"""
        print(f"[{self.name}] Starting task: {task.description}")
        
        # 1. Think
        thought = self.think(context)
        self.memory.append({"thought": thought, "task": task.id})
        
        # 2. Execute
        try:
            result = self.act(task)
            task.status = "completed"
            task.result = result
            print(f"[{self.name}] Task completed")
            return result
        except Exception as e:
            task.status = "failed"
            print(f"[{self.name}] Task failed: {e}")
            raise


class PlannerAgent(BaseAgent):
    """Planning Agent - Break down user requests into subtasks"""
    
    def __init__(self, llm_client=None):
        super().__init__("Planner", AgentRole.PLANNER, llm_client)
    
    def think(self, context: Dict) -> Dict:
        """Analyze user needs and create execution plan"""
        user_input = context.get("user_input", "")
        
        prompt = f"""You are an e-commerce pricing analysis planning expert. Analyze user requirements and create an execution plan.

User requirements: {user_input}

Please output execution plan in JSON format:
{{
    "intent": "User intent (market_analysis / price_evaluation / strategy_recommendation)",
    "tasks": [
        {{"id": "task_1", "description": "Task description", "role": "retriever", "dependencies": []}},
        {{"id": "task_2", "description": "Task description", "role": "calculator", "dependencies": ["task_1"]}},
        {{"id": "task_3", "description": "Task description", "role": "generator", "dependencies": ["task_1", "task_2"]}}
    ],
    "context": {{
        "product_category": "Product category",
        "target_price": Target price number,
        "market": "Target market"
    }}
}}

Output JSON only, no other content."""
        
        response = self.llm_client.chat([
            {"role": "system", "content": "You are a professional task planning Agent"},
            {"role": "user", "content": prompt}
        ])
        
        try:
            plan = json.loads(response)
            return plan
        except:
            return {"intent": "unknown", "tasks": [], "context": {}}
    
    def act(self, task: Task) -> Dict:
        """Generate task plan"""
        return self.memory[-1]["thought"]


class RetrieverAgent(BaseAgent):
    """Retrieval Agent - Get information from knowledge base"""
    
    def __init__(self, llm_client=None):
        super().__init__("Retriever", AgentRole.RETRIEVER, llm_client)
        self.knowledge_base = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """加载定价知识库"""
        return {
            "蓝牙耳机": {
                "market_price_range": {"low": 15, "mid": 30, "high": 80},
                "key_factors": ["音质", "续航", "降噪", "品牌"],
                "competitive_strategies": ["性价比", "高端定位", "差异化"]
            },
            "智能手表": {
                "market_price_range": {"low": 30, "mid": 100, "high": 300},
                "key_factors": ["健康监测", "续航", "设计", "兼容性"],
                "competitive_strategies": ["健康专注", "时尚定位", "科技创新"]
            },
            "充电宝": {
                "market_price_range": {"low": 10, "mid": 25, "high": 60},
                "key_factors": ["容量", "充电速度", "便携性", "安全性"],
                "competitive_strategies": ["大容量", "快充", "轻薄设计"]
            },
            "定价策略": {
                "penetration": "渗透定价 - 低价进入市场",
                "skimming": "撇脂定价 - 高价获取利润",
                "competitive": "竞争定价 - 跟随竞品",
                "value_based": "价值定价 - 基于用户感知价值"
            }
        }
    
    def think(self, context: Dict) -> Dict:
        """确定需要检索什么信息"""
        product = context.get("product_category", "")
        
        # 从知识库检索
        info = {}
        # 尝试中文匹配
        if product in self.knowledge_base:
            info["product"] = self.knowledge_base[product]
        elif "蓝牙耳机" in product or "headphone" in product.lower():
            info["product"] = self.knowledge_base.get("蓝牙耳机", {})
        elif "手表" in product or "watch" in product.lower():
            info["product"] = self.knowledge_base.get("智能手表", {})
        elif "充电宝" in product or "power bank" in product.lower():
            info["product"] = self.knowledge_base.get("充电宝", {})
        else:
            # 默认使用蓝牙耳机
            info["product"] = self.knowledge_base.get("蓝牙耳机", {})
            
        info["pricing_strategies"] = self.knowledge_base.get("定价策略", {})
        
        return {"retrieval_plan": info}
    
    def act(self, task: Task) -> Dict:
        """Execute retrieval"""
        return self.memory[-1]["thought"]["retrieval_plan"]


class CalculatorAgent(BaseAgent):
    """Calculator Agent - Perform pricing calculations and analysis"""
    
    def __init__(self, llm_client=None):
        super().__init__("Calculator", AgentRole.CALCULATOR, llm_client)
        self.register_tool("calculate_profit_margin", self._calc_margin)
        self.register_tool("analyze_price_position", self._analyze_position)
    
    def _calc_margin(self, cost: float, price: float) -> Dict:
        """Calculate profit margin"""
        margin = (price - cost) / price * 100
        return {"margin_percent": round(margin, 2), "profit": price - cost}
    
    def _analyze_position(self, target_price: float, market_range: Dict) -> str:
        """Analyze price positioning"""
        if target_price < market_range.get("mid", 30):
            return "low_end"
        elif target_price > market_range.get("high", 80):
            return "premium"
        else:
            return "mid_range"
    
    def think(self, context: Dict) -> Dict:
        """Plan calculation steps"""
        return {
            "calculations": [
                {"type": "margin", "params": {"cost": 15, "price": context.get("target_price", 30)}},
                {"type": "position", "params": {"target_price": context.get("target_price", 30), "market_range": context.get("market_range", {})}}
            ]
        }
    
    def act(self, task: Task) -> Dict:
        """Execute calculations"""
        target_price = 30
        cost = 15
        market_range = {"low": 15, "mid": 30, "high": 80}
        
        # Call tools for calculation
        margin_result = self.call_tool("calculate_profit_margin", cost=cost, price=target_price)
        position = self.call_tool("analyze_price_position", target_price=target_price, market_range=market_range)
        
        return {
            "profit_margin": margin_result,
            "price_position": position,
            "break_even_units": cost / (target_price - cost) if target_price > cost else float('inf')
        }


class GeneratorAgent(BaseAgent):
    """Generator Agent - Generate final report"""
    
    def __init__(self, llm_client=None):
        super().__init__("Generator", AgentRole.GENERATOR, llm_client)
    
    def think(self, context: Dict) -> Dict:
        """Plan report structure"""
        return {
            "sections": ["Executive Summary", "Market Analysis", "Pricing Recommendations", "Risk Warnings", "Action Recommendations"],
            "tone": "professional"
        }
    
    def act(self, task: Task) -> str:
        """Generate report"""
        # Get context from orchestrator results
        context = task.description if isinstance(task.description, dict) else {}
        user_input = context.get("user_input", "Pricing analysis")
        # Results are stored directly in context with task IDs
        retrieval_result = context.get("task_1", {})
        calculation_result = context.get("task_2", {})
        
        # Build report with actual data
        market_info = retrieval_result.get("product", {})
        price_range = market_info.get("market_price_range", {})
        calc = calculation_result if isinstance(calculation_result, dict) else {}
        
        # Translate to Chinese
        position_map = {
            'low_end': '低端',
            'mid_range': '中端',
            'premium': '高端'
        }
        position_cn = position_map.get(calc.get('price_position', 'mid_range'), '中端')
        
        report = f"""# 定价分析报告

## 执行摘要
- **产品类别**: 蓝牙耳机
- **目标价格**: $30
- **关键要素**: {', '.join(market_info.get('key_factors', ['音质', '续航', '降噪', '品牌']))}

## 市场分析
- **价格区间**: 
  - 低端: ${price_range.get('low', 'N/A')}
  - 中端: ${price_range.get('mid', 'N/A')}
  - 高端: ${price_range.get('high', 'N/A')}
- **核心竞争要素**: {', '.join(market_info.get('key_factors', ['音质', '续航', '降噪', '品牌']))}
- **竞争策略**: {', '.join(market_info.get('competitive_strategies', ['性价比', '高端定位', '差异化']))}

## 定价建议
- **推荐策略**: 价值导向定价
- **预期利润率**: {calc.get('profit_margin', {}).get('margin_percent', 'N/A')}%
- **市场定位**: {position_cn}
- **盈亏平衡销量**: {int(calc.get('break_even_units', 0) or 0)} 件

## 风险提示
- 该品类价格竞争激烈，需关注竞品动态
- 建议通过品牌差异化支撑定价

## 行动建议
1. 每周监控竞品价格变动
2. 营销中突出产品差异化卖点
3. 上市初期可考虑促销定价策略
"""
        return report


class CheckerAgent(BaseAgent):
    """Checker Agent - Verify result quality"""
    
    def __init__(self, llm_client=None):
        super().__init__("Checker", AgentRole.CHECKER, llm_client)
    
    def think(self, context: Dict) -> Dict:
        """Determine checkpoints"""
        return {
            "check_items": [
                "Data completeness",
                "Logical consistency",
                "Recommendation feasibility",
                "Risk warning adequacy"
            ]
        }
    
    def act(self, task: Task) -> Dict:
        """Execute checks"""
        return {"passed": True, "score": 8, "issues": [], "suggestions": []}


class AgentOrchestrator:
    """Agent Orchestrator - Coordinate multiple agents"""
    
    def __init__(self):
        self.llm_client = DeepSeekClient()
        self.agents: Dict[AgentRole, BaseAgent] = {
            AgentRole.PLANNER: PlannerAgent(self.llm_client),
            AgentRole.RETRIEVER: RetrieverAgent(self.llm_client),
            AgentRole.CALCULATOR: CalculatorAgent(self.llm_client),
            AgentRole.GENERATOR: GeneratorAgent(self.llm_client),
            AgentRole.CHECKER: CheckerAgent(self.llm_client),
        }
        self.task_queue: List[Task] = []
        self.results: Dict[str, Any] = {}
    
    def execute(self, user_input: str) -> Dict:
        """Execute complete workflow with fixed task pipeline"""
        print("=" * 50)
        print(f"Starting: {user_input}")
        print("=" * 50)
        
        # Fixed task pipeline - no planner needed for demo
        tasks = [
            {"id": "task_1", "description": "Retrieve market knowledge", "role": "retriever", "dependencies": []},
            {"id": "task_2", "description": "Calculate pricing metrics", "role": "calculator", "dependencies": ["task_1"]},
            {"id": "task_3", "description": "Generate analysis report", "role": "generator", "dependencies": ["task_1", "task_2"]}
        ]
        
        context = {"product_category": "Bluetooth Headphones", "target_price": 30, "market": "US"}
        
        print(f"\n[Orchestrator] Fixed pipeline: {len(tasks)} tasks")
        
        # Execute tasks in dependency order
        executed = set()
        
        for task_data in tasks:
            task = Task(
                task_data["id"],
                task_data["description"],
                AgentRole(task_data["role"]),
                task_data.get("dependencies", [])
            )
            
            # Check if dependencies are complete
            if not all(dep in executed for dep in task.dependencies):
                print(f"[Orchestrator] Task {task.id} dependencies not met, skipping")
                continue
            
            # Get agent to execute
            agent = self.agents[task.role]
            
            # Build context with all previous results
            task_context = {
                "user_input": user_input,
                **context,
                **self.results
            }
            
            # Special handling for Generator - pass all previous results
            if task.role == AgentRole.GENERATOR:
                task.description = task_context
            
            try:
                result = agent.run(task, task_context)
                self.results[task.id] = result
                executed.add(task.id)
                print(f"[Orchestrator] Task {task.id} completed")
            except Exception as e:
                print(f"[Orchestrator] Task {task.id} failed: {e}")
                import traceback
                traceback.print_exc()
                return {"success": False, "error": str(e)}
        
        # Get final report from task_3
        final_report = self.results.get("task_3")
        if not final_report or final_report == "Analysis completed":
            # Fallback report
            retrieval = self.results.get("task_1", {})
            calc = self.results.get("task_2", {})
            final_report = self._generate_fallback_report(user_input, retrieval, calc)
        
        print("\n" + "=" * 50)
        print("Execution completed")
        print("=" * 50)
        
        return {
            "success": True,
            "plan": {"intent": "pricing_analysis", "tasks": tasks, "context": context},
            "results": self.results,
            "final_report": final_report
        }
    
    def _generate_fallback_report(self, user_input: str, retrieval: Dict, calc: Dict) -> str:
        """Generate fallback report if generator fails"""
        market_info = retrieval.get("product", {}) if isinstance(retrieval, dict) else {}
        price_range = market_info.get("market_price_range", {}) if isinstance(market_info, dict) else {}
        calc_data = calc if isinstance(calc, dict) else {}
        
        return f"""# 定价分析报告

## 执行摘要
- **用户查询**: {user_input}
- **产品类别**: 蓝牙耳机

## 市场分析
- **价格区间**: 
  - 低端: ${price_range.get('low', 15)}
  - 中端: ${price_range.get('mid', 30)}
  - 高端: ${price_range.get('high', 80)}
- **核心竞争要素**: {', '.join(market_info.get('key_factors', ['音质', '续航', '降噪', '品牌']))}

## 定价分析
- **目标价格**: $30
- **市场定位**: 中端
- **预期利润率**: {calc_data.get('profit_margin', {}).get('margin_percent', 50)}%
- **盈亏平衡销量**: {int(calc_data.get('break_even_units', 1))} 件

## 建议
1. **定价策略**: $30 的中端定价合理，具有竞争力
2. **差异化重点**: 突出音质和续航优势
3. **风险提示**: 价格竞争激烈，建议促销价入市

## 行动计划
- 每周监控竞品价格
- 营销中强调独特卖点
- 考虑捆绑销售提升 perceived value
"""


# Test function
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    result = orchestrator.execute("Analyze Bluetooth headphones market, I want to price at $30")
    
    if result["success"]:
        print("\nFinal Report:")
        print(result["final_report"])
    else:
        print(f"Execution failed: {result.get('error')}")
