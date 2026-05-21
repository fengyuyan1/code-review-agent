/**
 * Java 代码质量问题示例
 */

import java.util.*;
import java.io.*;

public class JavaQualityIssues {

    // 问题1: 使用原始类型而不是泛型
    public List processUserList(List users) {
        List result = new ArrayList();
        for (int i = 0; i < users.size(); i++) {
            Map user = (Map) users.get(i);
            result.add(user.get("name") + " - " + user.get("email"));
        }
        return result;
    }

    // 问题2: 过度使用 synchronized，可能导致死锁
    public synchronized void updateUser(String id, String name) {
        synchronized (this) {
            User user = findUser(id);
            synchronized (user) {
                user.setName(name);
            }
        }
    }

    // 问题3: 忽略异常
    public void readFile(String path) {
        try {
            FileReader reader = new FileReader(path);
            BufferedReader br = new BufferedReader(reader);
            String line;
            while ((line = br.readLine()) != null) {
                System.out.println(line);
            }
            br.close();
        } catch (IOException e) {
            // 忽略异常
        }
    }

    // 问题4: 行过长
    public double calculateComplexValue(double a, double b, double c, double d, double e, double f) { return (a * b + c * d - e * f) / (a + b + c + d + e + f) * Math.sqrt(a * b * c * d * e * f); }

    // 问题5: 嵌套循环导致性能问题
    public void findDuplicates(int[] array) {
        for (int i = 0; i < array.length; i++) {
            for (int j = i + 1; j < array.length; j++) {
                for (int k = j + 1; k < array.length; k++) {
                    if (array[i] == array[j] && array[j] == array[k]) {
                        System.out.println("Found duplicate: " + array[i]);
                    }
                }
            }
        }
    }

    // 问题6: 使用反射而不考虑性能
    public Object invokeMethod(Object obj, String methodName) throws Exception {
        Class<?> clazz = obj.getClass();
        java.lang.reflect.Method method = clazz.getMethod(methodName);
        return method.invoke(obj);
    }

    // 问题7: 可变参数滥用
    public String concatenateStrings(String... strings) {
        String result = "";
        for (String s : strings) {
            result += s + " ";
        }
        return result;
    }

    // 问题8: 没有资源管理
    public String readFileContent(String path) throws IOException {
        FileReader reader = new FileReader(path);
        BufferedReader br = new BufferedReader(reader);
        String content = br.readLine();
        return content;
    }
}
